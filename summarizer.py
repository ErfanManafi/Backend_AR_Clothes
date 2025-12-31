import os

# --- تنظیمات ---
# پسوندهایی که باید خوانده شوند (می‌توانید موارد دلخواه را اضافه یا کم کنید)
ALLOWED_EXTENSIONS = {
    '.cs', '.xaml', '.csproj', '.sln', '.json', '.xml', '.txt', '.md', 
    '.razor', '.css', '.html', '.js', '.ts', '.py', '.config'
}

# پوشه‌هایی که باید نادیده گرفته شوند
EXCLUDED_DIRS = {'.git', '.vs', 'bin', 'obj', 'Properties', '__pycache__'}

# نام فایل خروجی
OUTPUT_FILENAME = 'project_summary.txt'
# ----------------

def create_project_summary():
    """
    اسکریپتی برای جمع‌آوری محتوای فایل‌های متنی یک پروژه در یک فایل واحد.
    """
    # 1. دریافت مسیر پوشه از کاربر
    folder_path = input("لطفاً مسیر کامل پوشه پروژه را وارد کرده و Enter را بزنید: ").strip()

    # 2. بررسی صحت مسیر
    if not os.path.isdir(folder_path):
        print(f"خطا: مسیر وارد شده '{folder_path}' یک پوشه معتبر نیست.")
        return

    # 3. تعیین مسیر فایل خروجی (در کنار پوشه پروژه)
    output_path = os.path.join(os.path.dirname(folder_path), OUTPUT_FILENAME)
    
    print(f"\nشروع به اسکن پوشه: {folder_path}")
    print(f"فایل خروجی در این مسیر ذخیره خواهد شد: {output_path}\n")

    try:
        # 4. باز کردن فایل خروجی برای نوشتن
        with open(output_path, 'w', encoding='utf-8') as summary_file:
            # 5. پیمایش تمام پوشه‌ها و فایل‌ها
            for root, dirs, files in os.walk(folder_path, topdown=True):
                # نادیده گرفتن پوشه‌های مشخص شده
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

                for filename in files:
                    # 6. بررسی پسوند فایل
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in ALLOWED_EXTENSIONS:
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, folder_path)
                        
                        print(f"  -> در حال خواندن: {relative_path}")

                        # 7. نوشتن هدر فایل (نام فایل)
                        summary_file.write(f"--- فایل: {relative_path} ---\n\n")

                        # 8. خواندن و نوشتن محتوای فایل با مدیریت خطا
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                                summary_file.write(content_file.read())
                        except Exception as e:
                            summary_file.write(f"[خطا در خواندن فایل: {e}]\n")
                        
                        summary_file.write("\n\n" + "="*80 + "\n\n")

        print(f"\nعملیات با موفقیت انجام شد!")
        print(f"فایل '{OUTPUT_FILENAME}' در کنار پوشه پروژه‌تان ایجاد شد.")

    except Exception as e:
        print(f"\nیک خطای غیرمنتظره رخ داد: {e}")

# اجرای تابع اصلی
if __name__ == "__main__":
    create_project_summary()