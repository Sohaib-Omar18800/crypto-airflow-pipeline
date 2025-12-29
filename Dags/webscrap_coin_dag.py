from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.sensors.sql import SqlSensor
from datetime import datetime
from datetime import date
import requests
from bs4 import BeautifulSoup

# {Task1 : WebScrap The Coin Currency From CoinGecko Website}


def get_coin_api():
    url = "https://www.coingecko.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('tbody')
    rows = table.find_all('tr')
    coins = []
    for row in rows:
        name = row.find('div', {
                        'class': "tw-block 2lg:tw-inline tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-medium"}).text.strip()
        price_dollarsign = row.find(
            'span', {'data-price-target': "price"}).text.strip()
        price = price_dollarsign.replace('$', '').replace(',', '')
        coins.append({'Date': date.today().strftime('%d/%m/%Y'), 'Time': datetime.now().strftime(
            "%H:%M:%S"), 'Name': name, 'Price': price})
    return coins

# {Task2 : Create Table in Postgres Server If Not Exist And Insert The Values}


def parse_coins(ti):
    COIN_LIST = ti.xcom_pull(task_ids='Get_Coins_From_Api')
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_db')
    create_table_sql_query = "CREATE TABLE IF NOT EXISTS crypto_prices(" \
        "index INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY," \
        "coin_name VARCHAR(25)," \
        "price NUMERIC," \
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    pg_hook.run(create_table_sql_query)
    rows = [(v['Name'], float(v['Price'])) for v in COIN_LIST]
    pg_hook.insert_rows(table='crypto_prices', rows=rows,
                        target_fields=['coin_name', 'price'])
    print(f"Successfully inserted {len(COIN_LIST)} coins into Postgres!")

# {Task3 :Alert In Case Faliure}


def email_failure_alert(context):
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    log_url = context['task_instance'].log_url
    execution_date = context['execution_date']

    subject = f"❌ Airflow Alert: Task Failed in {dag_id}"
    body = f"""
    <h3>Task Failed!</h3>
    <b>DAG:</b> {dag_id}<br>
    <b>Task:</b> {task_id}<br>
    <b>Date:</b> {execution_date}<br>
    <b>Log:</b> <a href='{log_url}'>Click here to see logs</a>
    """
    send_email(to=['example@email.com'],
               subject=subject, html_content=body)


default_args = {
    'owner': 'airflow',
    'email': ['example@email.com'],
    'email_on_failure': True,
    'email_on_success': False,
    'on_failure_callback': email_failure_alert,
    'retries': 1
}

with DAG(dag_id='Coin_Webscrap', description='WebScrap And Extract Crypto Currency', start_date=datetime(2025, 11, 25), schedule="* * * * *", catchup=False, default_args=default_args) as dag:
    task1 = PythonOperator(
        task_id='Get_Coins_From_Api',
        python_callable=get_coin_api
    )
    task2 = PythonOperator(
        task_id='Parse_Coins',
        python_callable=parse_coins
    )
    check_db_count = SqlSensor(
        task_id='Check_DB_Count_Sensor',
        conn_id='my_postgres_db',
        sql="SELECT COUNT(*) >= 5 FROM crypto_prices WHERE coin_name = 'BTC';",
        poke_interval=30,
        timeout=3600,
        mode='reschedule'
    )

    task1 >> task2 >> check_db_count
