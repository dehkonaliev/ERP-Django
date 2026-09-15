Creat an ERP system:

#Models:
1. Course:
  title
  duration (months)
  description
  lesson_price (price for one lesson)
2. Group:
  name
  teacher (FK)
  course (FK)
  level (month)
  teacher_share (part of the payment to teacher, 0.3, 0.4 or something like this, on frontend it will be shown like 30%, 35%, 40%)
3. Lesson:
  title
  group (FK)
  context (Text info)
  video (youtube link iframe)
4. Attendance:
  lesson (FK)
  student (FK)
  is_absent (default=False)
5. Homework:
  task (text task description)
  lesson (FK)
  file
6. Submission (By student)
  homework (FK)
  context (text context)
  file (file submission)
7. StudentInfo:
  balance
  xp
8. TeacherInfo:
  subject (Physics)
  balance
9. Payment:
  student (FK)
  amount
10. CustomUser:
  phone_number
  date_of_birth

Create CustomUser(AbstractUser) model
Only managers can create a user with password. Only manager can create a group and attach students into those groups. Managers can replenish student's balance.
Managers can view and monitor all system, attendance, students and teachers profiles. On student's profile show the groups attached, XPs, and balance for teachers- and managers or student's himself. 
On teacher's profile show groups, balance and everything related to teacher for managers and teacher's himself. 
Teachers creates lessons and homeworks and checks student's submissions. Based on the submission give XPs. 10XP for 100 points (points/100*10XP(integer)). Teacher can edit lessons and homeworks. 
Teacher can check attendance of students. When student participated in lesson, withdraw amount (lesson_price) from student's balance and replenish teacher's balance to amount (teacher_share*lesson_price)
Student can submit the answer to Homework and see groupmates as a list in the leaderboard. On leaderboard show studnets ordered by their XP and make it possible to filter by group and all.
Create great UX/UI. Try sleek and modern UI frontend. Add some missing parameters on models like created_at (updated_at if needed). 
Use FBV or View. Make understandable code. Write like a junior student. Don't use complicated syntax.
Use only Django (Templates, Forms and etc). Build section by section. Take your time

