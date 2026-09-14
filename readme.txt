ERP TIZIMI - QURILISH REJASI
=============================
Texnologiya: Django (templates, DRF yo'q) + SQLite. CustomUser rollari: student / teacher / manager (o'quvchi / o'qituvchi / rahbar).

Funksional to'plam (o'rta murakkablik):
- Rollarga asoslangan kirish va shaxsiy kabinetlar (student, teacher, manager)
- Guruhlar (sinflar) va guruhga yozilish boshqaruvi
- Kurslar + Darslar + Davomat
- Baholash / Natijalar
- Reyting (leaderboard) - baho va davomatdan ball yig'ish
- To'lovlar (stipendiya/oquy to'lovlarini hisobga olish)
- Rahbar (manager) uchun hisobotlar

----------------------------------------
INSTALLED_APPS (+ tavsiya etilgan yangi app'lar)
----------------------------------------
authentication - foydalanuvchi modeli, profil
groups        - guruhlar, guruhga yozilish     [MAVJUD app]
courses       - kurslar, darslar, davomat, baholar  [YANGI app]
leaderboard   - ballar, reyting yozuvlari      [MAVJUD app]
payments      - invoice (hisob), to'lovlar     [MAVJUD app]
core          - bosh sahifa/kabinet view'lari

----------------------------------------
MODELLAR
----------------------------------------

APP: authentication
  CustomUser(AbstractUser)  [mavjud]
    phone_number: CharField(13)
    user_role: CharField choices STUDENT/TEACHER/MANAGER

APP: groups
  Group  (guruh)
    name: CharField(100), unique            # guruh nomi
    description: TextField(blank)
    teacher: FK(User, related_name='taught_groups')   # guruh o'qituvchisi
    created_at: DateTimeField(auto_now_add)
    is_active: BooleanField(default=True)
    __str__ -> name

  Enrollment  (guruhga yozilish)
    group: FK(Group, related_name='enrollments')
    student: FK(User, related_name='enrollments')
    enrolled_at: DateTimeField(auto_now_add)
    status: CharField choices ACTIVE/COMPLETED/DROPPED, default ACTIVE
    constraints: unique (group, student)
    __str__ -> f"{student} in {group}"

APP: courses
  Course  (kurs)
    code: CharField(12), unique             # kurs kodi, masalan CS101
    title: CharField(150)                   # nomi
    description: TextField(blank)
    credit: PositiveSmallIntegerField(default 1)
    created_at

  Lesson  (dars)
    course: FK(Course, related_name='lessons')
    title: CharField(150)
    date: DateField(auto_now_add)           # dars sanasi
    duration_minutes: PositiveSmallIntegerField  # davomiyligi (daq)
    materials: FileField(blank) -> MEDIA_ROOT  # dars materiallari

  Attendance  (davomat)
    lesson: FK(Lesson, related_name='attendance')
    student: FK(User)
    status: CharField choices PRESENT/ABSENT/LATE/EXCUSED, default ABSENT
    marked_by: FK(User, null=True)          # kim belgiladi
    marked_at: DateTimeField(auto_now)
    constraints: unique (lesson, student)

  Grade  (baho)
    student: FK(User)
    course: FK(Course)
    enrollment: FK(Enrollment, null=True, blank=True)
    exam_type: CharField choices QUIZ/MIDTERM/FINAL/ASSIGNMENT
    score: DecimalField(max_digits 5, decimal_places 2, max 100)  # 100 ballik
    comment: CharField(blank)               # izoh
    graded_by: FK(User, null=True)          # kim baholadi
    graded_at: DateTimeField(auto_now_add)
    constraints: unique (student, course, exam_type)

APP: leaderboard
  PointsAward  (ball berish tarixi)
    student: FK(User)
    source: FK ContentType generic (bahodan yoki davomatdan)
    source_id: PositiveInteger
    points: SmallInteger                    # berilgan ball
    reason: CharField(200)                  # sabab
    awarded_at: DateTimeField(auto_now_add)

  hisoblash: umumiy ball - student bo'yicha aggregate so'rov
  LeaderboardEntry model ixtiyoriy: haftalik natijalar keshi (cache)
    student, week_start: DateField, total_points, rank

APP: payments
  Invoice  (to'lov hujjati)
    student: FK(User)
    title: CharField(120)                   # masalan "1-chorak to'lovi"
    amount: DecimalField(10,2)              # summa
    due_date: DateField                     # to'lash muddati
    issued_at auto_now_add                  # berilgan sana
    is_paid: BooleanField (to'lovlar orqali yoki hisoblab chiqiladi)

  Payment  (to'lov)
    invoice: FK(Invoice, related_name='payments')
    amount: DecimalField(10,2)              # to'langan summa
    method: CharField choices CASH/CARD/BANK_TRANSFER  (naqd/karta/bank)
    paid_at: DateTimeField(auto_now_add)    # to'lov vaqti
    received_by: FK(User, null=True)        # qabul qilgan xodim
    receipt_no: CharField unique            # chek raqami (generatsiya qilinadi)

  hisob: invoice.balance = amount - sum(payments)  # qolgan qarz

----------------------------------------
UMUMIY YORDAMCHI KODLAR
----------------------------------------
- ModelManager: dashboard ma'lumotlarini user_role bo'yicha filtrlash
- mixins.py: ManagerRequiredMixin, TeacherRequiredMixin (rullar tekshiruvi)
- utils.py: generate_receipt_no(), compute_leaderboard(), award_points()

----------------------------------------
VIEW'LAR / URL'LAR / TEMPLATE'LAR (har modul uchun)
----------------------------------------
AUTHENTICATION
  - ro'yxatdan o'tish (faqat manager), login, logout
  - profil ko'rish + o'z profilini tahrirlash
  - logindan keyin rolga qarab qayta yo'naltirish (home)
  - parolni o'zgartirish (django ichki)

KABINETLAR (DASHBOARD)
  - student: mening guruhlarim, kelgusi darslar, mening baholarim,
            mening reyting o'rnum, qarzdor to'lovlarim
  - teacher: mening guruhlarim, davomatni belgilash, baho kiritish, reyting
  - manager: statistika (o'quvchilar/guruhlar/daromad), moliyaviy hisobot

GROUPS
  - ro'yxat, yaratish, o'zgartirish, o'chirish (manager)
  - batafsil: guruh a'zolari, darslar
  - guruhga o'quvchi qo'shish / olib tashlash (manager)

COURSES
  - kurs ro'yxati/batafsil (teacher + manager)
  - darslar ro'yxati + dars qo'shish (teacher)
  - davomat varaqasi: guruhdagi o'quvchilar, chekboxlar (teacher)
  - baho kiritish: har kurs+o'quvchi, har exam_type uchun forma (teacher)

LEADERBOARD (REYTING)
  - umumiy reyting sahifasi (top N ball bo'yicha)
  - haftalik / barcha vaqt rejimlari

PAYMENTS (TO'LOVLAR)
  - invoice ro'yxati, yaratish (manager), batafsil
  - to'lovni qayd qilish (manager) -> balans yangilanadi
  - student: mening invoice'larim + qarzdorlik

----------------------------------------
TEMPLATE TUZILISHI
----------------------------------------
templates/
  base.html (sidebar + navbar, rolga qarab menyu)
  registration/ (login.html, signup.html, password_change.html)
  components/ (pagination.html, messages.html)
  groups/, courses/, leaderboard/, payments/
  dashboard/ (student.html, teacher.html, manager.html)
Static: oddiy css (yoki Bootstrap 5 CDN orqali)

CSS qarori: Bootstrap 5 CDN dan foydalanish (o'rta daraja, tez ishlash).

----------------------------------------
FILE / MEDIA SOZLASH
----------------------------------------
- MEDIA_URL = '/media/', MEDIA_ROOT = BASE_DIR/'media'
- LOGIN_URL, LOGIN_REDIRECT_URL sozlanadi
- AUTH_USER_MODEL allaqachon authentication.CustomUser ga ulangan

----------------------------------------
QURILISH TARTIBI (bosqichlar)
----------------------------------------
1. Modellar: yuqoridagilarni yozish + makemigrations/migrate (admin'ga qo'shish)
2. Base template + static + login/logout/profil + kabinetlar
3. Groups moduli (CRUD + yozilish) boshidan oxirigacha
4. Courses + Lessons + Attendance (teacher ish jarayoni)
5. Baho kiritish + signals orqali reyting ballari
6. Leaderboard view'lari (ball jamlash)
7. Payments (invoice, to'lov, balans)
8. Manager hisobotlari/kabinetni yakunlash
9. Permissions + rollar tekshiruvi, test ma'lumotlar (fixtures/scripts)

----------------------------------------
RUXSATLAR XARITASI (PERMISSIONS)
----------------------------------------
Amal                        student  teacher  manager
O'z kabinetini ko'rish        x        x        x
Guruh ro'yxati/batafsil       x        x        x
Guruh yaratish/tahrirlash     -        -        x
Yozilish qo'shish/o'chirish   -        -        x
Dars qo'shish                -        x        -
Davomat belgilash            -        x        -
Baho kiritish                -        x        -
Reytingni ko'rish            x        x        x
O'z invoice'larini ko'rish   x        -        -
Invoice yaratish/to'lov      -        -        x
Hisobotlarni ko'rish         -        -        x

----------------------------------------
SIGNALS (avtomatik jarayonlar)
----------------------------------------
- post_save Grade -> reyting ball berish (score/10)
- post_save Payment -> invoice balansini / is_paid ni yangilash
- post_save Enrollment -> kichik ball berish (ixtiyoriy)

----------------------------------------
KENGAYTIRMA (o'rta darajadan yuqori) - kerak bo'lmasa o'tkazib yuboring
----------------------------------------
- Jadval/reja (schedule), bildirishnomalar (email), takroriy invoice
- Hisobotlarni CSV chiqarish, grafiklar, API endpoint'lar