from flask import Flask, render_template, request,jsonify
import plotly.graph_objs as go
import plotly.offline as pyo
import requests

app = Flask(__name__)

# Пример данных о пользователе и успеваемости
user_data = {
    'name': 'Иван Иванов',
    'attendance': ['Математика', 'Физика', 'Химия'],
    'schedule': {
        'Monday': ['Математика', 'Физика'],
        'Tuesday': ['Химия', 'Литература'],
        'Wednesday': ['История', 'География'],
        'Thursday': ['Физика', 'Математика'],
        'Friday': ['Литература', 'Химия']
    },
    'grades': [85, 90, 78, 92, 88]  # Оценки по предметам
}

@app.route('/')
def index():
    return render_template('index.html', user_data=user_data)

@app.route('/dashboard')
def dashboard():
    courses_response = requests.get('http://89.111.153.166:8081/api/v1/courses')
    courses = courses_response.json()
    # Пример данных пользователя (можно заменить на реальные данные)
    user = {
        'name': 'Иван Петров',
        'attendance': ['Математика', 'История'],
        'schedule': {
            'Понедельник': ['Алгебра', 'Физика'],
            'Среда': ['Химия']
        }
    }
    # Создание графика успеваемости
    grades = user_data['grades']
    subjects = user_data['attendance']
    
    fig = go.Figure(data=[go.Bar(x=subjects, y=grades)])
    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    
    return render_template('dashboard.html', 
                           user=user,
                           graph=graph_html,
                           courses=courses)
    
    
@app.route('/course/<int:course_id>')
def course_detail(course_id):
    # Получаем детали конкретного курса
    response = requests.get(f'http://89.111.153.166:8081/api/v1/courses/{course_id}')

    course = response.json()
    response1 = requests.get(f"http://89.111.153.166:8081/api/v1/courses/{course_id}/lessons")
    lessons = response1.json()
    return render_template('course_detail.html', course=course, lessons =lessons)


@app.route('/lessons/<int:course_id>/<int:lesson_id>')
def lesson_detail(course_id, lesson_id):
    # Получаем детали конкретного урока
    response = requests.get(f'http://89.111.153.166:8081/api/v1/courses/{course_id}/lessons/{lesson_id}')
    lessons = response.json()
    print(lessons)
    return render_template('lessons.html', lesson = lessons)
    


@app.route('/pro')
def pro_users():
    try:
        # Получаем данные с API
        response = requests.get("http://89.111.153.166:8081/api/v1/users", timeout=10)
        response.raise_for_status()
        users_data = response.json()
        
        # Обрабатываем специальный случай с fullName
        processed_users = []
        for user in users_data:
            user['fullName'] = None if user.get('fullName') == 'null null' else user.get('fullName')
            processed_users.append(user)
        
        return render_template('pro.html', users=processed_users)
    
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}", 500
    except Exception as e:
        return f"Server Error: {str(e)}", 500


@app.route('/categories')
def create_category():
        payload = {
            "name": "Системное администрование2",
            "description": "Администрирование систем"
        }

        # Отправляем запрос к API
        response = requests.post(
            "http://89.111.153.166:8081/api/v1/categories",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )

        # Обрабатываем ответ
        if response.status_code == 201:
            return jsonify(response.json()), 201
            
        return jsonify({
            "error": "API request failed",
            "status_code": response.status_code,
            "message": response.text
        }), response.status_code

if __name__ == '__main__':
    app.run(debug=True)