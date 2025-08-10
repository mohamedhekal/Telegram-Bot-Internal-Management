import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
import config

class DatabaseManager:
    def __init__(self, db_path="invoice_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات مع إعدادات محسنة"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول الفواتير
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_number TEXT UNIQUE,
                employee_name TEXT,
                client_name TEXT,
                client_phone TEXT,
                governorate TEXT,
                nearest_point TEXT,
                quantity INTEGER,
                price REAL,
                total_sales REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'employee',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول كلمات مرور الموظفين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الإحصائيات اليومية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT,
                date DATE,
                total_orders INTEGER DEFAULT 0,
                total_quantity INTEGER DEFAULT 0,
                total_sales REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_name, date)
            )
        ''')
        
        # جدول المرتجعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                receipt_number TEXT,
                employee_name TEXT,
                return_type TEXT CHECK(return_type IN ('full', 'partial')),
                returned_quantity INTEGER,
                returned_amount REAL,
                remaining_amount REAL,
                return_reason TEXT,
                processed_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_invoice(self, invoice_data):
        """إضافة فاتورة جديدة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO invoices (
                    receipt_number, employee_name, client_name, client_phone,
                    governorate, nearest_point, quantity, price, total_sales, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['receipt_number'],
                invoice_data['employee_name'],
                invoice_data['client_name'],
                invoice_data['client_phone'],
                invoice_data['governorate'],
                invoice_data['nearest_point'],
                invoice_data['quantity'],
                invoice_data['price'],
                invoice_data['total_sales'],
                invoice_data['notes']
            ))
            
            # تحديث الإحصائيات اليومية
            self.update_daily_stats(invoice_data['employee_name'])
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطأ في إضافة الفاتورة: {e}")
            return False
    
    def update_daily_stats(self, employee_name):
        """تحديث الإحصائيات اليومية"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            # حساب إجماليات اليوم
            cursor.execute('''
                SELECT COUNT(*), SUM(quantity), SUM(total_sales)
                FROM invoices 
                WHERE employee_name = ? AND DATE(created_at) = ?
            ''', (employee_name, today))
            
            result = cursor.fetchone()
            total_orders = result[0] or 0
            total_quantity = result[1] or 0
            total_sales = result[2] or 0
            
            # إدراج أو تحديث الإحصائيات
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (employee_name, date, total_orders, total_quantity, total_sales)
                VALUES (?, ?, ?, ?, ?)
            ''', (employee_name, today, total_orders, total_quantity, total_sales))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {e}")
    
    def get_employee_monthly_stats(self, employee_name, month=None, year=None):
        """الحصول على إحصائيات الموظف الشهرية"""
        try:
            if month is None:
                month = datetime.now().month
            if year is None:
                year = datetime.now().year
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # الحصول على الفواتير للشهر المحدد
            cursor.execute('''
                SELECT * FROM invoices 
                WHERE employee_name = ? 
                AND strftime('%m', created_at) = ? 
                AND strftime('%Y', created_at) = ?
                ORDER BY created_at DESC
            ''', (employee_name, f"{month:02d}", str(year)))
            
            invoices = cursor.fetchall()
            
            # حساب الإجماليات
            total_orders = len(invoices)
            total_quantity = sum(invoice[7] for invoice in invoices)  # quantity column (index 7)
            total_sales = sum(invoice[9] for invoice in invoices)    # total_sales column (index 9)
            
            conn.close()
            
            return {
                'total_orders': total_orders,
                'total_quantity': total_quantity,
                'total_sales': total_sales,
                'invoices': invoices
            }
        except Exception as e:
            print(f"خطأ في الحصول على الإحصائيات: {e}")
            return None
    
    def get_all_invoices_for_shipping(self, days=1):
        """الحصول على جميع الفواتير لملف شركة التوصيل"""
        try:
            conn = self.get_connection()
            
            # الحصول على الفواتير للآخر X أيام
            query = '''
                SELECT * FROM invoices 
                WHERE created_at >= datetime('now', '-{} days')
                ORDER BY created_at DESC
            '''.format(days)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
        except Exception as e:
            print(f"خطأ في الحصول على فواتير التوصيل: {e}")
            return None
    
    def create_shipping_excel(self, days=1):
        """إنشاء ملف Excel لشركة التوصيل باستخدام قالب محدد"""
        try:
            df = self.get_all_invoices_for_shipping(days)
            if df is None or df.empty:
                print("لا توجد فواتير لإنشاء ملف التوصيل.")
                return None

            template_path = config.SHIPPING_TEMPLATE_FILE
            
            if not os.path.exists(template_path):
                print(f"خطأ: قالب شركة التوصيل غير موجود في المسار: {template_path}")
                return self._create_new_shipping_excel(df)

            try:
                workbook = openpyxl.load_workbook(template_path)
                sheet = workbook.active
            except Exception as e:
                print(f"خطأ في تحميل قالب Excel: {e}. سيتم إنشاء ملف جديد.")
                return self._create_new_shipping_excel(df)

            # مسح البيانات الموجودة مع الحفاظ على العناوين
            for row in sheet.iter_rows(min_row=2):
                for cell in row:
                    cell.value = None
            for row_idx in range(sheet.max_row, 1, -1):
                if all(cell.value is None for cell in sheet[row_idx]):
                    sheet.delete_rows(row_idx)

            # إضافة البيانات الجديدة
            data_to_append = []
            for index, row in df.iterrows():
                data_to_append.append([
                    row['receipt_number'],
                    row['client_name'],
                    row['client_phone'],
                    row['governorate'],
                    row['nearest_point'],
                    row['quantity'],
                    row['price'],
                    "لا",
                    row['notes']
                ])

            for row_data in data_to_append:
                sheet.append(row_data)

            output_filename = f"shipping_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            workbook.save(output_filename)
            
            print(f"تم إنشاء ملف التوصيل بنجاح: {output_filename}")
            return output_filename

        except Exception as e:
            print(f"خطأ في إنشاء ملف التوصيل باستخدام القالب: {e}")
            return None

    def _create_new_shipping_excel(self, df):
        """إنشاء ملف Excel جديد في حالة عدم وجود القالب"""
        try:
            filename = f"shipping_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Shipping Data', index=False)
                
                # تنسيق الملف
                workbook = writer.book
                worksheet = writer.sheets['Shipping Data']
                
                # تنسيق العناوين
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = Alignment(horizontal="center")
                
                # تعديل عرض الأعمدة
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return filename
        except Exception as e:
            print(f"خطأ في إنشاء ملف التوصيل: {e}")
            return None
    
    def add_user(self, telegram_id, username, full_name, role="employee"):
        """إضافة مستخدم جديد"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (telegram_id, username, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', (telegram_id, username, full_name, role))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المستخدم: {e}")
            return False
    
    def get_user_role(self, telegram_id):
        """الحصول على دور المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT role FROM users WHERE telegram_id = ?', (telegram_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else "employee"
        except Exception as e:
            print(f"خطأ في الحصول على دور المستخدم: {e}")
            return "employee"
    
    def get_all_employees_stats(self, month=None, year=None):
        """الحصول على إحصائيات جميع الموظفين"""
        try:
            if month is None:
                month = datetime.now().month
            if year is None:
                year = datetime.now().year
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    employee_name,
                    COUNT(*) as total_orders,
                    SUM(quantity) as total_quantity,
                    SUM(total_sales) as total_sales
                FROM invoices 
                WHERE strftime('%m', created_at) = ? 
                AND strftime('%Y', created_at) = ?
                GROUP BY employee_name
                ORDER BY total_sales DESC
            ''', (f"{month:02d}", str(year)))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"خطأ في الحصول على إحصائيات الموظفين: {e}")
            return []

    def get_employee_stats_by_date_range(self, employee_name, start_date, end_date):
        """الحصول على إحصائيات الموظف لفترة زمنية محددة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM invoices 
                WHERE employee_name = ? 
                AND DATE(created_at) BETWEEN ? AND ?
                ORDER BY created_at DESC
            ''', (employee_name, start_date, end_date))
            
            invoices = cursor.fetchall()
            
            # حساب الإجماليات
            total_orders = len(invoices)
            total_quantity = sum(invoice[7] for invoice in invoices)  # quantity column
            total_sales = sum(invoice[9] for invoice in invoices)    # total_sales column
            
            conn.close()
            
            return {
                'total_orders': total_orders,
                'total_quantity': total_quantity,
                'total_sales': total_sales,
                'invoices': invoices,
                'start_date': start_date,
                'end_date': end_date
            }
        except Exception as e:
            print(f"خطأ في الحصول على الإحصائيات: {e}")
            return None

    def get_all_employees_stats_by_date_range(self, start_date, end_date):
        """الحصول على إحصائيات جميع الموظفين لفترة زمنية محددة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    employee_name,
                    COUNT(*) as total_orders,
                    SUM(quantity) as total_quantity,
                    SUM(total_sales) as total_sales
                FROM invoices 
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY employee_name
                ORDER BY total_sales DESC
            ''', (start_date, end_date))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"خطأ في الحصول على إحصائيات الموظفين: {e}")
            return []

    def create_statistics_excel(self, stats_data, report_type="monthly", date_info=""):
        """إنشاء ملف إكسل للإحصائيات"""
        try:
            # إنشاء DataFrame
            if report_type == "all_employees":
                df = pd.DataFrame(stats_data['employees'])
                filename = f"employees_statistics_{date_info}_{int(time.time())}.xlsx"
            else:
                df = pd.DataFrame([stats_data])
                filename = f"employee_statistics_{stats_data.get('employee_name', 'unknown')}_{date_info}_{int(time.time())}.xlsx"
            
            # إنشاء ملف الإكسل
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Statistics', index=False)
                
                # الحصول على ورقة العمل
                worksheet = writer.sheets['Statistics']
                
                # تنسيق العناوين
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=1, column=col)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center")
                
                # تنسيق الأرقام
                for row in range(2, len(df) + 2):
                    for col in range(1, len(df.columns) + 1):
                        cell = worksheet.cell(row=row, column=col)
                        cell.alignment = Alignment(horizontal="center")
            
            return filename
            
        except Exception as e:
            print(f"خطأ في إنشاء ملف الإكسل: {e}")
            return None

    def set_employee_password(self, employee_name, password):
        """تعيين كلمة مرور للموظف"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO employee_passwords (employee_name, password, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (employee_name, password))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطأ في تعيين كلمة المرور: {e}")
            return False

    def verify_employee_password(self, employee_name, password):
        """التحقق من كلمة مرور الموظف"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT password FROM employee_passwords 
                WHERE employee_name = ?
            ''', (employee_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0] == password
            return False
        except Exception as e:
            print(f"خطأ في التحقق من كلمة المرور: {e}")
            return False

    def get_employee_password(self, employee_name):
        """الحصول على كلمة مرور الموظف"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT password FROM employee_passwords 
                WHERE employee_name = ?
            ''', (employee_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"خطأ في الحصول على كلمة المرور: {e}")
            return None

    def has_password(self, employee_name):
        """التحقق من وجود كلمة مرور للموظف"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM employee_passwords 
                WHERE employee_name = ?
            ''', (employee_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] > 0
        except Exception as e:
            print(f"خطأ في التحقق من وجود كلمة المرور: {e}")
            return False

    def get_all_passwords(self):
        """الحصول على جميع كلمات المرور"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT employee_name, password FROM employee_passwords 
                ORDER BY employee_name
            ''')
            
            result = cursor.fetchall()
            conn.close()
            
            return result
        except Exception as e:
            print(f"خطأ في الحصول على كلمات المرور: {e}")
            return []

    def delete_employee_password(self, employee_name):
        """حذف كلمة مرور الموظف"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM employee_passwords 
                WHERE employee_name = ?
            ''', (employee_name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطأ في حذف كلمة المرور: {e}")
            return False

    # ==================== دوال إدارة المرتجعات ====================
    
    def get_invoice_by_receipt(self, receipt_number):
        """الحصول على فاتورة برقم الإيصال"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # تنظيف رقم الإيصال من المسافات
            receipt_number = receipt_number.strip()
            
            # إذا كان الرقم بدون بادئة INV-، أضفها
            if not receipt_number.startswith('INV-'):
                receipt_number = f"INV-{receipt_number}"
            
            cursor.execute('''
                SELECT id, receipt_number, employee_name, client_name, 
                       quantity, price, total_sales, created_at
                FROM invoices 
                WHERE receipt_number = ?
            ''', (receipt_number,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'receipt_number': result[1],
                    'employee_name': result[2],
                    'client_name': result[3],
                    'quantity': result[4],
                    'price': result[5],
                    'total_sales': result[6],
                    'created_at': result[7]
                }
            return None
        except Exception as e:
            print(f"خطأ في الحصول على الفاتورة: {e}")
            return None

    def add_return(self, return_data):
        """إضافة مرتجع جديد"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO returns (
                    invoice_id, receipt_number, employee_name, return_type,
                    returned_quantity, returned_amount, remaining_amount,
                    return_reason, processed_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                return_data['invoice_id'],
                return_data['receipt_number'],
                return_data['employee_name'],
                return_data['return_type'],
                return_data['returned_quantity'],
                return_data['returned_amount'],
                return_data['remaining_amount'],
                return_data['return_reason'],
                return_data['processed_by']
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطأ في إضافة المرتجع: {e}")
            return False

    def get_returns_by_employee(self, employee_name, start_date=None, end_date=None):
        """الحصول على مرتجعات موظف معين"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT r.*, i.client_name, i.quantity as original_quantity, i.total_sales as original_total
                FROM returns r
                JOIN invoices i ON r.invoice_id = i.id
                WHERE r.employee_name = ?
            '''
            params = [employee_name]
            
            if start_date and end_date:
                query += ' AND DATE(r.created_at) BETWEEN ? AND ?'
                params.extend([start_date, end_date])
            
            query += ' ORDER BY r.created_at DESC'
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            returns = []
            for row in results:
                returns.append({
                    'id': row[0],
                    'invoice_id': row[1],
                    'receipt_number': row[2],
                    'employee_name': row[3],
                    'return_type': row[4],
                    'returned_quantity': row[5],
                    'returned_amount': row[6],
                    'remaining_amount': row[7],
                    'return_reason': row[8],
                    'processed_by': row[9],
                    'created_at': row[10],
                    'client_name': row[11],
                    'original_quantity': row[12],
                    'original_total': row[13]
                })
            
            return returns
        except Exception as e:
            print(f"خطأ في الحصول على المرتجعات: {e}")
            return []

    def get_employee_stats_with_returns(self, employee_name, month=None, year=None):
        """الحصول على إحصائيات الموظف مع خصم المرتجعات"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # الحصول على إحصائيات الفواتير
            if month and year:
                cursor.execute('''
                    SELECT COUNT(*) as total_invoices,
                           SUM(quantity) as total_quantity,
                           SUM(total_sales) as total_sales
                    FROM invoices 
                    WHERE employee_name = ? 
                    AND strftime('%m', created_at) = ? 
                    AND strftime('%Y', created_at) = ?
                ''', (employee_name, f"{month:02d}", str(year)))
            else:
                current_month = datetime.now().month
                current_year = datetime.now().year
                cursor.execute('''
                    SELECT COUNT(*) as total_invoices,
                           SUM(quantity) as total_quantity,
                           SUM(total_sales) as total_sales
                    FROM invoices 
                    WHERE employee_name = ? 
                    AND strftime('%m', created_at) = ? 
                    AND strftime('%Y', created_at) = ?
                ''', (employee_name, f"{current_month:02d}", str(current_year)))
            
            invoice_stats = cursor.fetchone()
            
            # الحصول على إحصائيات المرتجعات
            if month and year:
                cursor.execute('''
                    SELECT SUM(returned_quantity) as total_returned_quantity,
                           SUM(returned_amount) as total_returned_amount
                    FROM returns 
                    WHERE employee_name = ? 
                    AND strftime('%m', created_at) = ? 
                    AND strftime('%Y', created_at) = ?
                ''', (employee_name, f"{month:02d}", str(year)))
            else:
                current_month = datetime.now().month
                current_year = datetime.now().year
                cursor.execute('''
                    SELECT SUM(returned_quantity) as total_returned_quantity,
                           SUM(returned_amount) as total_returned_amount
                    FROM returns 
                    WHERE employee_name = ? 
                    AND strftime('%m', created_at) = ? 
                    AND strftime('%Y', created_at) = ?
                ''', (employee_name, f"{current_month:02d}", str(current_year)))
            
            return_stats = cursor.fetchone()
            
            conn.close()
            
            # حساب الإحصائيات النهائية
            total_invoices = invoice_stats[0] or 0
            total_quantity = invoice_stats[1] or 0
            total_sales = invoice_stats[2] or 0
            
            total_returned_quantity = return_stats[0] or 0
            total_returned_amount = return_stats[1] or 0
            
            # خصم المرتجعات
            final_quantity = total_quantity - total_returned_quantity
            final_sales = total_sales - total_returned_amount
            
            return {
                'employee_name': employee_name,
                'total_invoices': total_invoices,
                'total_quantity': total_quantity,
                'total_sales': total_sales,
                'returned_quantity': total_returned_quantity,
                'returned_amount': total_returned_amount,
                'final_quantity': final_quantity,
                'final_sales': final_sales
            }
        except Exception as e:
            print(f"خطأ في الحصول على الإحصائيات مع المرتجعات: {e}")
            return None

    def get_all_employees_stats_with_returns(self, month=None, year=None):
        """الحصول على إحصائيات جميع الموظفين مع خصم المرتجعات"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # الحصول على جميع الموظفين
            cursor.execute('''
                SELECT DISTINCT employee_name FROM invoices
                UNION
                SELECT DISTINCT employee_name FROM returns
            ''')
            
            employees = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # الحصول على إحصائيات كل موظف
            all_stats = []
            for employee in employees:
                stats = self.get_employee_stats_with_returns(employee, month, year)
                if stats:
                    all_stats.append(stats)
            
            return all_stats
        except Exception as e:
            print(f"خطأ في الحصول على إحصائيات جميع الموظفين: {e}")
            return [] 