# 🛡️ Ransomware Detection System - دليل التشغيل

## بنية المشروع / Project Structure

```
project/
├── gui.py              ← الواجهة الرسومية (شغّل ده)
├── demo_attack.py      ← سكريبت المحاكاة الآمنة
├── main.py             ← تشغيل الـ backend بدون GUI (للتجربة)
├── config.py           ← الإعدادات المركزية
├── detection_engine.py ← محرك كشف التهديدات
├── requirements.txt    ← المكتبات المطلوبة
├── monitor/
│   ├── __init__.py
│   ├── handler.py      ← معالج أحداث الملفات
│   ├── alerts.py       ← نظام التنبيهات
│   ├── behavior.py     ← تحليل السلوك والـ entropy
│   └── logger.py       ← تسجيل الأحداث JSONL
├── logs/               ← ملفات اللوجز (تُنشأ تلقائياً)
└── watched_folder/     ← المجلد المُراقَب
```

---

## متطلبات التشغيل / Requirements

- Python 3.10 أو أحدث
- المكتبات: `watchdog`, `psutil`

---

## تثبيت المكتبات / Install Libraries

```bash
pip install -r requirements.txt
```

أو بشكل مباشر:
```bash
pip install watchdog psutil
```

**ملاحظة:** tkinter مدمجة مع Python ولا تحتاج تثبيت.
إذا ظهر خطأ في tkinter:
- Windows: أعد تثبيت Python وتأكد من تفعيل خيار "tcl/tk"
- Linux: `sudo apt install python3-tk`
- Mac: `brew install python-tk`

---

## طريقة التشغيل / How to Run

### 1️⃣ تشغيل الـ GUI

```bash
cd project
python gui.py
```

### 2️⃣ اضغط "▶ Start Monitoring" في الـ GUI

### 3️⃣ تشغيل الديمو (في نافذة ثانية)

```bash
cd project
python demo_attack.py
```

### 4️⃣ شاهد التنبيهات في الـ GUI 🎉

---

## شرح الـ GUI / GUI Explanation

| القسم | الوظيفة |
|-------|---------|
| **Header** | عنوان المشروع + مؤشر الحالة الكبير + الأزرار |
| **Statistics** | عداد الملفات (Created / Modified / Deleted / Total) |
| **System Info** | مسار المجلد المُراقَب وملف اللوج |
| **Threat Level** | مستوى التهديد مع الـ entropy score |
| **Real-Time Alerts** | التنبيهات الفورية ملونة حسب النوع |
| **Real-Time Logs** | سجل كل حدث في المجلد |
| **Footer** | وقت آخر تحديث + حالة النظام |

### حالات النظام / System States:

| الحالة | اللون | المعنى |
|--------|-------|--------|
| IDLE | رمادي | لم تبدأ المراقبة |
| MONITORING - SAFE | أخضر | يراقب ولا يوجد تهديد |
| SUSPICIOUS ACTIVITY | برتقالي | نشاط مشبوه (modified≥20, entropy≥6) |
| ATTACK DETECTED | أحمر | هجوم فدية محتمل (modified≥50, entropy≥7) |

---

## كيف يعمل النظام / How Detection Works

### 1. مراقبة الملفات (watchdog)
النظام يراقب مجلد `watched_folder` باستخدام مكتبة watchdog وهي تبلغه فوراً عن:
- إنشاء ملف جديد (created)
- تعديل ملف (modified)
- حذف ملف (deleted)

### 2. تحليل السلوك (BehaviorAnalyzer)
لكل حدث، يحسب:
- **Modification Rate**: كم ملف اتعدل في آخر 10 ثواني
- **Shannon Entropy**: مقياس عشوائية محتوى الملف (0-8)
  - ملف عادي: entropy ≈ 3-5 (فيه تكرار)
  - ملف مشفر: entropy ≈ 7-8 (عشوائي تماماً)

### 3. تصنيف التهديد (detection_engine)
```python
if modified >= 50 and entropy >= 7.0 → DANGEROUS (هجوم!)
elif modified >= 20 and entropy >= 6.0 → SUSPICIOUS (مشبوه)
else → NORMAL (طبيعي)
```

### 4. إرسال التنبيهات
- للـ GUI عبر Queue آمنة (thread-safe)
- للـ log file بصيغة JSONL

---

## الأسئلة المتوقعة في المناقشة / Expected Discussion Questions

**1. ما هو الـ Shannon Entropy؟**
> مقياس عشوائية البيانات من 0 إلى 8.
> الملف العادي فيه تكرار → entropy منخفضة
> الملف المشفر عشوائي تماماً → entropy = 8
> الـ ransomware بتشفر الملفات فبتحول entropy من 3 لـ 8

**2. ليه بتستخدم Queue بين الـ GUI والـ backend؟**
> Tkinter مش thread-safe. لو حدّثنا الـ GUI مباشرة من thread تاني، البرنامج هيكرش.
> الـ Queue بتنقل البيانات بأمان بين الـ threads.

**3. ما الفرق بين watchdog و psutil؟**
> watchdog: بتراقب تغييرات الملفات
> psutil: بتعطي معلومات عن الـ processes الشغالة

**4. ليه الديمو آمن؟**
> لأنه شغال في مجلد watched_folder فقط.
> مش بيلمس ملفات النظام أو مجلدات المستخدم.
> المحتوى المكتوب مجرد bytes عشوائية وليس فيروس حقيقي.

**5. ما هي خطوات الهجوم التي يحاكيها الديمو؟**
> Phase 1: جمع الملفات (Enumeration)
> Phase 2: التشفير السريع (Encryption) - high entropy
> Phase 3: إعادة التسمية (Renaming .locked)
> Phase 4: طلب الفدية (Ransom Note)

---

## ملاحظات للعرض / Presentation Tips

1. افتح الـ GUI أولاً وشرح كل قسم
2. اضغط Start Monitoring وانتظر ثانية
3. في نافذة ثانية شغّل demo_attack.py
4. اشرح كل phase بينما التنبيهات بتظهر
5. اشرح كيف تغير اللون من أخضر لأحمر

---

*Graduation Project 2026 - Ransomware Detection System*
