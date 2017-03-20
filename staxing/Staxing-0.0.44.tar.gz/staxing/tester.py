"""helper test."""

from time import sleep
from random import randint

try:
    from assignment import Assignment
except ImportError:
    try:
        from .assignment import Assignment
    except ImportError:
        from staxing.assignment import Assignment
try:
    from helper import Helper, Teacher, Student, Admin, ContentQA, User
except ImportError:
    try:
        from .helper import Helper, Teacher, Student, Admin, ContentQA, User
    except ImportError:
        from staxing.helper import Helper, Teacher, Student, Admin, \
            ContentQA, User

helper = Helper
user = User
teacher = Teacher
student = Student
admin = Admin
content = ContentQA
assignment = Assignment
rand = randint

print('HELPER CLASS')
with Helper() as helper:
    helper.set_window_size(1300, 700)
    helper.change_wait_time(5)
    print(helper.wait_time)
    print(helper.date_string())
    print(helper.date_string(5))
    print(helper.date_string(str_format='%Y-%m-%d'))
    print(helper.date_string(12, '%Y%m%d'))
    print('GET google.com')
    helper.get('https://www.google.com/')
    print(helper.get_window_size())
    print(helper.get_window_size('height'))
    print(helper.get_window_size('width'))
    print('starting sleep 1')
    helper.sleep()
    print('ending sleep 1')
    print('starting sleep 5')
    helper.sleep(5)
    print('ending sleep 5')

print('USER CLASS')
with User('', '', '') as user:
    user.set_window_size(1300, 700)
    print('Tutor login')
    user.login('https://tutor-qa.openstax.org', 'student01', 'staxly16')
    print('Tutor logout')
    user.logout()
    print('Accounts login')
    user.login('https://accounts-qa.openstax.org', 'student02', 'staxly16')
    print('Accounts logout')
    user.logout()
    print('User login')
    user.login('https://tutor-qa.openstax.org', 'student01', 'staxly16')
    print('Select course by title')
    user.select_course(title='College Physics with Courseware')
    print('Go to course list')
    user.goto_course_list()
    print('Select course by appearance')
    user.select_course(appearance='college_physics')
    print('Open the reference book')
    user.view_reference_book()

print('TEACHER CLASS')
with Teacher(use_env_vars=True) as teacher:
    teacher.set_window_size(1300, 700)
    print('Tutor login')
    teacher.login(username='teacher01', password='staxly16')
    print('Select course by title')
    teacher.select_course(title='College Physics with Courseware')
    sleep(5)
    print('Add a reading assignment')
    teacher.add_assignment(
        'reading',
        args={
            'title': 'reading test %s' % randint(0, 100000),
            'description': 'new reading',
            'periods': {'all': (teacher.date_string(),
                                teacher.date_string(randint(0, 10)))},
            'reading_list': ['ch1', 'ch2', '3.1'],
            'status': 'draft',
        }
    )
    sleep(3)
    teacher.add_assignment(
        'homework',
        args={
            'title': 'homework test %s' % randint(0, 100000),
            'description': 'new homework',
            'periods': {'all': (teacher.date_string(),
                                teacher.date_string(randint(0, 10)))},
            'problems': {
                '1.3': (2, 5),
                '1.2': 2,
                '1.1': 'all',
                'tutor': 2,
            },
            'status': 'draft',
        }
    )
    sleep(3)
    teacher.add_assignment(
        'external',
        args={}
    )
    print('Go to the performance forecast')
    try:
        teacher.goto_performance_forecast()
        sleep(5)
    except:
        print('No performance forecast in Concept Coach')
    print('Go to the calendar')
    teacher.goto_calendar()
    sleep(5)
    print('Go to the course roster')
    teacher.goto_course_roster()
    sleep(5)
    print('Add a section to the class')
    section = Assignment.rword(10)
    sleep(5)

print('Switch to CC')
with Teacher(username='teacher100',
             password='staxly16',
             site='https://tutor-qa.openstax.org/') as teacher:
    teacher.set_window_size(1300, 700)
    teacher.login()
    teacher.select_course(title='Introduction to Sociology ' +
                          '2e with Concept Coachs')
    print('Get an enrollment code')
    teacher.goto_course_roster()
    teacher.add_course_section(section)
    code = teacher.get_enrollment_code(section)
    try:
        print('Enrollment Code: "%s"' % code)
    except:
        print('No enrollment code in Tutor')
    sleep(2)

print('TUTOR STUDENT CLASS')
with Student(use_env_vars=True) as student:
    student.set_window_size(1300, 700)
    student.login()
    student.select_course(title='College Physics')
    print('Practice')
    student.practice()
    sleep(2)

print('CC STUDENT CLASS')
with Student(use_env_vars=True) as student:
    student.set_window_size(1300, 700)
    sleep(2)

print('ADMIN CLASS')
with Admin(use_env_vars=True) as admin:
    admin.set_window_size(1300, 700)
    sleep(2)
    admin.login()
    admin.goto_admin_control()
    sleep(2)
    admin.goto_course_list()
    sleep(2)
    admin.goto_ecosystems()
    sleep(2)

print('CONTENTQA CLASS')
with ContentQA(use_env_vars=True) as content:
    content.set_window_size(1300, 700)
    sleep(2)
