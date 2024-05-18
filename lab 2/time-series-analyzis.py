import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest



def parse_files():
    users = 'new_users.csv'
    views = 'page_views.csv'
    pageSessions = 'pages-sessions.csv'

    df_users = pd.read_csv(users)
    df_views = pd.read_csv(views)
    df_pageSessions = pd.read_csv(pageSessions)


    splitted_users = df_users['Day,New_Users'].str.split(',', expand=True)
    df_users['Day'] = splitted_users[0]
    df_users['New_Users'] = df_users['Day,New_Users'].str.extract(r'"(.*)"')
    df_users.drop(columns=['Day,New_Users'], inplace=True)


    splitted_views = df_views['Day,Pageviews'].str.split(',', expand=True)
    df_views['Day'] = splitted_views[0]
    df_views['Pageviews'] = df_views['Day,Pageviews'].str.extract(r'"(.*)"')
    df_views.drop(columns=['Day,Pageviews'], inplace=True)


    splitted_Pages_Session = df_pageSessions['Day,Pages_Session'].str.split(',', expand=True)
    df_pageSessions['Day'] = splitted_Pages_Session[0]
    df_pageSessions['Pages_Session'] = splitted_Pages_Session[1]
    df_pageSessions.drop(columns=['Day,Pages_Session'], inplace=True)

    # Перетворення стовпця дати у формат datetime
    df_users['Day'] = pd.to_datetime(df_users['Day'], format='%m/%d/%y', errors='coerce')
    df_views['Day'] = pd.to_datetime(df_views['Day'], format='%m/%d/%y', errors='coerce')
    df_pageSessions['Day'] = pd.to_datetime(df_pageSessions['Day'], format='%m/%d/%y', errors='coerce')

    df_users['New_Users'] = df_users['New_Users'].str.replace(',', '').astype(int, errors='ignore')
    df_views['Pageviews'] = df_views['Pageviews'].str.replace(',', '').astype(int, errors='ignore')
    df_pageSessions['Pages_Session'] = df_pageSessions['Pages_Session'].astype(float, errors='ignore')


    return df_users, df_views, df_pageSessions


def moving_average_anomaly(series, window_size=30, threshold=3):
    rolling_mean = series.rolling(window=window_size).mean()
    rolling_std = series.rolling(window=window_size).std()
    anomalies = series[(series - rolling_mean).abs() > (threshold * rolling_std)]
    return anomalies

def z_score_anomaly(series, threshold=3):
    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std
    anomalies = series[np.abs(z_scores) > threshold]
    return anomalies

def plot_anomalies(normal_data, anomalies, title):
    plt.figure(figsize=(12, 6))
    plt.plot(normal_data.index, normal_data, label='Normal Data')
    plt.scatter(anomalies.index, anomalies, color='red', label='Anomalies')
    plt.title(title)
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    df_users, df_views, df_pageSessions = parse_files()
    print(df_users)
    print(df_views)
    print(df_pageSessions)

#Пошук аномалій за допомогою moving average
    data_users = df_users['New_Users']
    data_users.dropna(inplace=True)
    data_users = pd.to_numeric(data_users, errors='coerce')

    new_users_anomalies = moving_average_anomaly(data_users)

    data_views = df_views['Pageviews']
    data_views.dropna(inplace=True)
    data_views = pd.to_numeric(data_views, errors='coerce')

    views_anomalies = moving_average_anomaly(data_views)

    data_pageSessions = df_pageSessions['Pages_Session']
    data_pageSessions.dropna(inplace=True)
    data_pageSessions = pd.to_numeric(data_pageSessions, errors='coerce')

    pageSessions_anomalies = moving_average_anomaly(data_pageSessions)

    plot_anomalies(data_users, new_users_anomalies, 'New Users')
    plot_anomalies(data_views, views_anomalies, 'Page Views')
    plot_anomalies(data_pageSessions, pageSessions_anomalies, 'Pages per Session')

#Пошук аномалій за допомогою One-Class SVM
    model_users = OneClassSVM(nu=0.15)  # nu - параметр, що визначає очікувану частку аномалій у даних
    data_users_reshaped = data_users.values.reshape(-1, 1)
    model_users.fit(data_users_reshaped)

    # Прогнозування аномалій
    svm_user_anomalies = model_users.predict(data_users_reshaped)
    svm_user_anomalies_series = pd.Series(svm_user_anomalies, index=data_users.index)
    svm_user_anomalies_series = svm_user_anomalies_series[svm_user_anomalies_series == -1]

    plot_anomalies(data_users, data_users[svm_user_anomalies_series.index], 'New Users SVM anomalies')

    model_views = OneClassSVM(nu=0.01)  # nu - параметр, що визначає очікувану частку аномалій у даних
    data_views_reshaped = data_views.values.reshape(-1, 1)
    model_views.fit(data_views_reshaped)

    # Прогнозування аномалій
    svm_views_anomalies = model_views.predict(data_views_reshaped)
    svm_views_anomalies_series = pd.Series(svm_views_anomalies, index=data_views.index)
    svm_views_anomalies_series = svm_views_anomalies_series[svm_views_anomalies_series == -1]

    plot_anomalies(data_views, data_views[svm_views_anomalies_series.index], 'Sessions SVM anomalies')

    model_pageSessions = OneClassSVM(nu=0.04)  # nu - параметр, що визначає очікувану частку аномалій у даних
    data_pageSessions_reshaped = data_pageSessions.values.reshape(-1, 1)
    model_pageSessions.fit(data_pageSessions_reshaped)

    # Прогнозування аномалій
    svm_pageSessions_anomalies = model_pageSessions.predict(data_pageSessions_reshaped)
    svm_pageSessions_anomalies_series = pd.Series(svm_pageSessions_anomalies, index=data_pageSessions.index)
    svm_pageSessions_anomalies_series = svm_pageSessions_anomalies_series[svm_pageSessions_anomalies_series == -1]

    plot_anomalies(data_pageSessions, data_pageSessions[svm_pageSessions_anomalies_series.index], 'Pages per Session SVM anomalies')

#Пошук аномалій за допомогою IsolationForest
    # Навчання моделі Isolation Forest
    IsolationForest_users_model = IsolationForest(contamination=0.01)  # contamination - частка аномалій у даних
    IsolationForest_users_model.fit(data_users_reshaped)

    # Прогнозування аномалій
    IsolationForest_users_anomalies = IsolationForest_users_model.predict(data_users_reshaped)
    IsolationForest_users_anomalies_series = pd.Series(IsolationForest_users_anomalies, index=data_users.index)
    IsolationForest_users_anomalies_series = IsolationForest_users_anomalies_series[IsolationForest_users_anomalies_series == -1]

    # Виклик функції для побудови графіка
    plot_anomalies(data_users, data_users[IsolationForest_users_anomalies_series.index], 'New Users Isolation Forest anomalies')

    # Навчання моделі Isolation Forest
    IsolationForest_views_model = IsolationForest(contamination=0.01)  # contamination - частка аномалій у даних
    IsolationForest_views_model.fit(data_views_reshaped)

    # Прогнозування аномалій
    IsolationForest_views_anomalies = IsolationForest_views_model.predict(data_views_reshaped)
    IsolationForest_views_anomalies_series = pd.Series(IsolationForest_views_anomalies, index=data_views.index)
    IsolationForest_views_anomalies_series = IsolationForest_views_anomalies_series[IsolationForest_views_anomalies_series == -1]

    plot_anomalies(data_views, data_views[IsolationForest_views_anomalies_series.index], 'Views Isolation Forest anomalies')

    # Навчання моделі Isolation Forest
    IsolationForest_pageSessions_model = IsolationForest(contamination=0.01)  # contamination - частка аномалій у даних
    IsolationForest_pageSessions_model.fit(data_pageSessions_reshaped)

    # Прогнозування аномалій
    IsolationForest_pageSessions_anomalies = IsolationForest_pageSessions_model.predict(data_pageSessions_reshaped)
    IsolationForest_pageSessions_anomalies_series = pd.Series(IsolationForest_pageSessions_anomalies, index=data_pageSessions.index)
    IsolationForest_pageSessions_anomalies_series = IsolationForest_pageSessions_anomalies_series[IsolationForest_pageSessions_anomalies_series == -1]

    plot_anomalies(data_pageSessions, data_pageSessions[IsolationForest_pageSessions_anomalies_series.index], 'Pages per Session Isolation Forest anomalies')

# Пошук аномалій за допомогою Z-Score
    Z_Score_user_anomalies = z_score_anomaly(data_users)
    plot_anomalies(data_users, Z_Score_user_anomalies, 'New Users Z-Score Anomalies')

    Z_Score_views_anomalies = z_score_anomaly(data_views)
    plot_anomalies(data_views, Z_Score_views_anomalies, 'Views Z-Score Anomalies')

    Z_Score_pageSessions_anomalies = z_score_anomaly(data_pageSessions)
    plot_anomalies(data_pageSessions, Z_Score_pageSessions_anomalies, 'Pages per Session Z-Score Anomalies')