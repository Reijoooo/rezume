import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Загрузка данных
    file_path = 'sales_data.csv'  # Замените на путь к вашему файлу данных
    data = pd.read_csv(file_path, encoding='ISO-8859-1')  # Используйте подходящую кодировку

    # Преобразование столбца с датами в формат datetime
    data['ORDERDATE'] = pd.to_datetime(data['ORDERDATE'])

    # Агрегирование данных по дате заказа для получения ежедневных сумм продаж
    daily_sales = data.groupby('ORDERDATE')['SALES'].sum().reset_index()

    # Подготовка данных для модели Prophet
    # Prophet требует столбцы с названиями 'ds' для дат и 'y' для прогнозируемых значений
    df_prophet = daily_sales.rename(columns={'ORDERDATE': 'ds', 'SALES': 'y'})

    # Создание и обучение модели Prophet
    model = Prophet()
    model.fit(df_prophet)

    # Создание датафрейма для будущих дат (например, на 6 месяцев вперед)
    future = model.make_future_dataframe(periods=180)

    # Выполнение прогноза
    forecast = model.predict(future)

    # Визуализация результатов прогноза
    fig, ax = plt.subplots(figsize=(10, 6))
    # Рисование исторических данных
    ax.plot(df_prophet['ds'], df_prophet['y'], 'k.', label='Historical Data')
    # Выделение прогнозируемой части данных
    ax.plot(forecast['ds'], forecast['yhat'], label='Forecast', color='red')
    # Заполнение доверительного интервала
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='pink', alpha=0.5)
    ax.legend()
    plt.show()

    # Визуализация компонентов временного ряда (тренд, сезонность)
    model.plot_components(forecast)
    plt.show()

    # Вывод последних прогнозов для оценки
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())