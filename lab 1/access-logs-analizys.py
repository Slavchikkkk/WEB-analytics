from user_agents import parse
import geoip2.database
import pandas as pd
import re
import seaborn as sns
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt


reader = geoip2.database.Reader('C:\\Users\\m.shovak\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages\\_geoip_geolite2\\GeoLite2-City.mmdb')


def parse_log_line(line):
    # Регулярний вираз для вилучення потрібних даних
    pattern = r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]+)" "([^"]+)"'

    # Застосовуємо регулярний вираз
    match = re.match(pattern, line)
    # Якщо відповідність не знайдено, повертаємо None
    if not match:
        return None

    # Вилучаємо дані з відповідності
    groups = match.groups()
    user_agent = parse(groups[10])
    os = user_agent.os.family
    return {
        "IP": groups[0],
        "Client": groups[2],
        "Timestamp": groups[3],
        "Method": groups[4],
        "URL": groups[5],
        "Protocol": groups[6],
        "Status": int(groups[7]),
        "Size": int(groups[8]),
        "Referer": groups[9],
        "User-Agent": groups[10],
        "OS": os
    }


# Функція для зчитування access.log та створення масиву та датафрейму
def read_log_file(file_path):
    # Читаємо файл по рядках
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Парсимо кожен рядок та створюємо список словників
    parsed_data = [parse_log_line(line) for line in lines]

    # Видаляємо None, якщо такі є
    parsed_data = [data for data in parsed_data if data is not None]
    #print(parsed_data)

    # Створюємо DataFrame зі списку словників
    df = pd.DataFrame(parsed_data)
    return df

def show_unique_bots(log_df):
    log_df['Bot'] = log_df['User-Agent'].apply(lambda x: next(
        (bot for bot in ['Googlebot', 'Bingbot', 'Yahoo! Slurp', 'DuckDuckBot', 'Baiduspider'] if bot in x), None))
    unique_bots = log_df.groupby('Bot')['IP'].nunique()
    print(unique_bots)
    return log_df


def show_unique_users_per_date(log_df):
    # Перетворення стовпця Timestamp у формат дати
    log_df['Timestamp'] = pd.to_datetime(log_df['Timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
    # Створення нового стовпця з датами
    log_df['Date'] = log_df['Timestamp'].dt.date

    # Групування за днями та підрахунок унікальних користувачів для кожного дня
    unique_users_per_day = log_df.groupby('Date')['IP'].nunique()
    print(unique_users_per_day)

def show_unique_users_agents(log_df):
    unique_user_agents = log_df.groupby('User-Agent')['IP'].nunique().sort_values(ascending=False)
    print(unique_user_agents)


def show_unique_os(log_df):
    unique_os = log_df.groupby('OS')['IP'].nunique()
    print(unique_os)

# Функція для отримання країни за IP-адресою через GeoIP сервіс
def identify_city(ip_address):
    try:
        response = reader.city(ip_address)
        return response.city.name
    except geoip2.errors.AddressNotFoundError:
        return None

# Функція для додавання колонки з містом до датафрейму
def add_city_column(log_df):
    log_df['City'] = log_df['IP'].apply(identify_city)


def show_unique_city(log_df):
    add_city_column(log_df)
    unique_city = log_df.groupby('City')['IP'].nunique()
    print(unique_city)

def show_anomalies(log_df):
    ip_addresses = log_df["IP"]

    # Ініціалізуємо LabelEncoder
    label_encoder = LabelEncoder()

    # Кодуємо рядки IP-адрес у числові ідентифікатори
    encoded_ip_addresses = label_encoder.fit_transform(ip_addresses)

    # Навчання моделі Local Outlier Factor
    lof_model = LocalOutlierFactor(contamination=0.05)  # contamination - очікувана частка аномалій
    predictions = lof_model.fit_predict(encoded_ip_addresses.reshape(-1, 1))

    # Додаємо прогнози аномалій у DataFrame
    log_df['LOF_Predictions'] = predictions
    anomalies = log_df[log_df['LOF_Predictions'] == -1]
    print("Anomalies:")
    print(anomalies)

    # Вибір аномальних даних
    anomalies = log_df[log_df['LOF_Predictions'] == -1]

    # Побудова гістограм для кожної колонки аномальних даних
    for column in anomalies.columns:
        if column != 'LOF_Predictions':  # Пропускаємо колонку з прогнозами аномалій
            plt.figure(figsize=(10, 6))
            sns.histplot(anomalies[column], kde=True)
            plt.title(f'Distribution of {column} in Anomalous Data')
            plt.xlabel(column)
            plt.ylabel('Frequency')
            plt.show()


if __name__ == "__main__":
    log_file_path = "C:\\Users\\m.shovak\\Desktop\\Studying\\WEB analytics\\lab 1\\access1.log"
    log_df = read_log_file(log_file_path)
    log_df = show_unique_bots(log_df)
    show_unique_users_per_date(log_df)
    show_unique_users_agents(log_df)
    show_unique_os(log_df)
    show_unique_city(log_df)
    show_anomalies(log_df)

