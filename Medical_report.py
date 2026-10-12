import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, csv, os, hashlib
from datetime import date, datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "medical_store.db"
INVOICE_DIR = APP_DIR / "invoices"
INVOICE_DIR.mkdir(exist_ok=True)

# नमूना डेटा: दाम, बैच और एक्सपायरी केवल डेमो के लिए हैं। बिक्री से पहले सत्यापित करें।
PRODUCTS = [
("Paracetamol 500 mg", "Tablet", "Analgesic", "Demo Pharma", "P500A", 1.50, "2027-12-31", 120),
("Paracetamol 650 mg", "Tablet", "Analgesic", "Demo Pharma", "P650B", 2.20, "2027-10-31", 100),
("Ibuprofen 400 mg", "Tablet", "Pain relief", "Sample Labs", "IB400C", 3.00, "2027-09-30", 80),
("Cetirizine 10 mg", "Tablet", "Antihistamine", "Sample Labs", "CT10D", 1.25, "2028-02-29", 90),
("ORS Sachet", "Powder sachet", "Rehydration", "Demo Pharma", "ORS05E", 18.00, "2027-08-31", 60),
("Vitamin C 500 mg", "Tablet", "Supplement", "Wellness Demo", "VC500F", 2.00, "2028-01-31", 100),
("Vitamin D3 60000 IU", "Capsule", "Supplement", "Wellness Demo", "VD60G", 12.00, "2027-11-30", 40),
("Calcium + D3", "Tablet", "Supplement", "Wellness Demo", "CALD8H", 5.00, "2028-03-31", 75),
("Omeprazole 20 mg", "Capsule", "Gastro", "Sample Labs", "OM20J", 3.50, "2027-12-31", 60),
("Pantoprazole 40 mg", "Tablet", "Gastro", "Sample Labs", "PN40K", 4.00, "2027-10-31", 70),
("Antacid chewable", "Tablet", "Gastro", "Demo Pharma", "ANTL1L", 1.00, "2027-07-31", 100),
("Loperamide 2 mg", "Capsule", "Gastro", "Demo Pharma", "LOP2M", 2.50, "2027-09-30", 35),
("Dextromethorphan syrup", "Syrup 100 ml", "Cough", "Sample Labs", "DEXN", 65.00, "2027-08-31", 24),
("Cough lozenges", "Lozenge", "Cough", "Sample Labs", "COUGP", 2.00, "2027-12-31", 80),
("Saline nasal drops", "Drops 10 ml", "Nasal care", "Demo Pharma", "SALQ", 28.00, "2027-11-30", 30),
("Antiseptic solution", "Solution 100 ml", "First aid", "Care Demo", "ANTSR", 45.00, "2028-01-31", 25),
("Povidone iodine ointment", "Ointment 15 g", "First aid", "Care Demo", "PVR", 38.00, "2027-10-31", 20),
("Calamine lotion", "Lotion 100 ml", "Skin care", "Care Demo", "CALU", 55.00, "2027-12-31", 22),
("Clotrimazole 1% cream", "Cream 15 g", "Skin care", "Care Demo", "CLOT V", 42.00, "2028-03-31", 18),
("Mupirocin 2% ointment", "Ointment 5 g", "Skin care", "Care Demo", "MUPW", 75.00, "2027-09-30", 12),
("Zinc oxide cream", "Cream 20 g", "Skin care", "Care Demo", "ZINX", 48.00, "2027-11-30", 16),
("Artificial tears", "Eye drops 10 ml", "Eye care", "Sample Labs", "EYEY", 60.00, "2027-08-31", 15),
("Lubricating eye gel", "Eye gel 10 g", "Eye care", "Sample Labs", "GELZ", 85.00, "2028-02-29", 10),
("B-complex", "Tablet", "Supplement", "Wellness Demo", "BC1A1", 2.50, "2027-12-31", 80),
("Iron + folic acid", "Tablet", "Supplement", "Wellness Demo", "IFA1B", 3.00, "2028-01-31", 60),
("Multivitamin", "Tablet", "Supplement", "Wellness Demo", "MUL1C", 4.00, "2027-10-31", 50),
("Azithromycin 500 mg", "Tablet", "Antibiotic - prescription", "Sample Labs", "AZI1D", 18.00, "2027-09-30", 30),
("Amoxicillin 500 mg", "Capsule", "Antibiotic - prescription", "Sample Labs", "AMO1E", 8.00, "2027-12-31", 30),
("Cephalexin 500 mg", "Capsule", "Antibiotic - prescription", "Sample Labs", "CEP1F", 10.00, "2027-11-30", 20),
("Metformin 500 mg", "Tablet", "Prescription", "Demo Pharma", "MET1G", 2.00, "2028-02-29", 70),
("Amlodipine 5 mg", "Tablet", "Prescription", "Demo Pharma", "AML1H", 1.50, "2027-10-31", 60),
("Losartan 50 mg", "Tablet", "Prescription", "Demo Pharma", "LOS1J", 3.50, "2028-01-31", 40),
("Atorvastatin 10 mg", "Tablet", "Prescription", "Demo Pharma", "ATO1K", 4.00, "2027-12-31", 45),
("Levothyroxine 50 mcg", "Tablet", "Prescription", "Sample Labs", "LEV1L", 1.20, "2027-08-31", 40),
("Montelukast 10 mg", "Tablet", "Prescription", "Sample Labs", "MON1M", 5.00, "2027-11-30", 25),
("Salbutamol inhaler", "Inhaler", "Prescription", "Sample Labs", "SAL1N", 110.00, "2027-09-30", 12),
("Insulin syringe", "Syringe", "Medical supply", "Care Demo", "INS1P", 12.00, "2028-03-31", 50),
("Digital thermometer", "Device", "Medical supply", "Care Demo", "DIG1Q", 180.00, "2030-12-31", 10),
("Cotton roll", "Pack 100 g", "Medical supply", "Care Demo", "COT1R", 35.00, "2029-12-31", 30),
("Gauze dressing", "Pack", "Medical supply", "Care Demo", "GAU1S", 25.00, "2029-12-31", 40),
("Adhesive bandage", "Pack 10", "Medical supply", "Care Demo", "BAN1T", 20.00, "2029-12-31", 50),
("Surgical gloves", "Pair", "Medical supply", "Care Demo", "GLV1U", 15.00, "2029-12-31", 60),
("Hand sanitizer", "Bottle 100 ml", "Hygiene", "Care Demo", "SAN1V", 40.00, "2028-04-30", 30),
("Face mask", "Pack 5", "Medical supply", "Care Demo", "MSK1W", 25.00, "2029-12-31", 100),
("Vitamin B12 500 mcg", "Tablet", "Supplement", "Wellness Demo", "B12500X", 3.00, "2028-03-31", 60),
("Magnesium 250 mg", "Tablet", "Supplement", "Wellness Demo", "MG250Y", 4.50, "2027-12-31", 40),
("Psyllium husk", "Powder 100 g", "Gastro", "Demo Pharma", "PSY100Z", 95.00, "2028-01-31", 18),
("Lactulose syrup", "Syrup 100 ml", "Gastro", "Demo Pharma", "LAC100AA", 80.00, "2027-10-31", 14),
("Domperidone 10 mg", "Tablet", "Prescription", "Sample Labs", "DOM10AB", 2.50, "2027-09-30", 30),
("Meclizine 25 mg", "Tablet", "Motion sickness", "Sample Labs", "MEC25AC", 3.00, "2028-02-29", 24),
("Fexofenadine 120 mg", "Tablet", "Antihistamine", "Sample Labs", "FEX120AD", 5.00, "2027-11-30", 30),
("Loratadine 10 mg", "Tablet", "Antihistamine", "Sample Labs", "LOR10AE", 2.00, "2028-01-31", 36),
("Hydrocortisone 1% cream", "Cream 10 g", "Skin care", "Care Demo", "HYD1AF", 32.00, "2027-12-31", 15),
("Aloe vera gel", "Gel 100 g", "Skin care", "Care Demo", "ALO100AG", 70.00, "2028-04-30", 20),
("ORS ready solution", "Bottle 200 ml", "Rehydration", "Demo Pharma", "ORS200AH", 28.00, "2027-07-31", 24),
("Glucose powder", "Pack 100 g", "Nutrition", "Wellness Demo", "GLU100AJ", 30.00, "2028-02-29", 30),
("Topical pain relief gel", "Gel 30 g", "Topical", "Care Demo", "PAI30AK", 65.00, "2027-10-31", 16),
("Diclofenac 50 mg", "Tablet", "Pain relief - prescription", "Sample Labs", "DIC50AL", 3.00, "2027-08-31", 25),
("Naproxen 250 mg", "Tablet", "Pain relief - prescription", "Sample Labs", "NAP250AM", 4.00, "2027-12-31", 20),
("Hydrogen peroxide 3%", "Solution 100 ml", "First aid", "Care Demo", "HYP3AN", 35.00, "2028-01-31", 20),
("Zinc 20 mg", "Tablet", "Supplement", "Wellness Demo", "ZIN20AP", 2.00, "2027-11-30", 50),
]

class StoreDB:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row
        self.db.execute('''CREATE TABLE IF NOT EXISTS medicines(
          id INTEGER PRIMARY KEY, name TEXT, form TEXT, category TEXT, manufacturer TEXT,
          batch TEXT UNIQUE, price REAL, expiry TEXT, stock INTEGER, reorder_level INTEGER DEFAULT 10,
          barcode TEXT DEFAULT '', prescription TEXT DEFAULT 'Check local rules', storage TEXT DEFAULT 'As per label')''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS sales(
          invoice TEXT PRIMARY KEY, sold_at TEXT, customer TEXT, phone TEXT, total REAL, file TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS sale_items(
          id INTEGER PRIMARY KEY, invoice TEXT, medicine_id INTEGER, name TEXT, qty INTEGER, unit_price REAL, line_total REAL)''')
        if self.db.execute('SELECT COUNT(*) FROM medicines').fetchone()[0] == 0:
            for p in PRODUCTS:
                name, form, category, maker, batch, price, expiry, stock = p
                self.db.execute('INSERT INTO medicines(name,form,category,manufacturer,batch,price,expiry,stock,barcode,prescription,storage) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                    (name, form, category, maker, batch, price, expiry, stock, batch, 'Prescription category: verify applicable law' if 'prescription' in category.lower() else 'Follow label / pharmacist guidance', 'Store as printed on pack'))
            self.db.commit()

class Login(tk.Tk):
    def __init__(self):
        super().__init__(); self.title('MediDesk | Sign in'); self.geometry('440x420'); self.resizable(False,False); self.configure(bg='#101827')
        box = tk.Frame(self, bg='#182437', padx=36, pady=34); box.place(relx=.5,rely=.5,anchor='center',width=360,height=340)
        tk.Label(box,text='MEDIDESK',font=('Segoe UI',22,'bold'),fg='#56d6bc',bg='#182437').pack(pady=(6,2))
        tk.Label(box,text='Medical Store Billing & Inventory',font=('Segoe UI',10),fg='#a9b8ca',bg='#182437').pack(pady=(0,24))
        tk.Label(box,text='Username',anchor='w',fg='#dce6f2',bg='#182437').pack(fill='x')
        self.user=ttk.Entry(box); self.user.pack(fill='x',pady=(5,14)); self.user.insert(0,'admin')
        tk.Label(box,text='Password',anchor='w',fg='#dce6f2',bg='#182437').pack(fill='x')
        self.pw=ttk.Entry(box,show='•'); self.pw.pack(fill='x',pady=(5,18)); self.pw.bind('<Return>',lambda e:self.login())
        ttk.Button(box,text='Sign in',command=self.login).pack(fill='x',ipady=6)
        tk.Label(box,text='Demo login: admin / admin123',font=('Segoe UI',9),fg='#8595aa',bg='#182437').pack(pady=15)
    def login(self):
        if self.user.get().strip()=='admin' and self.pw.get()=='admin123':
            self.destroy(); app=StoreApp(); app.mainloop()
        else: messagebox.showerror('Login failed','Username or password is incorrect.')

class StoreApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.db=StoreDB(); self.title('MediDesk | Store Console'); self.geometry('1280x780'); self.minsize(1050,650); self.configure(bg='#f2f5f9'); self.cart={}
        style=ttk.Style(self); style.theme_use('clam'); style.configure('Treeview',rowheight=28,font=('Segoe UI',9)); style.configure('Treeview.Heading',font=('Segoe UI',9,'bold')); style.configure('TButton',font=('Segoe UI',9))
        top=tk.Frame(self,bg='#101827',height=64); top.pack(fill='x'); top.pack_propagate(False)
        tk.Label(top,text='  MEDIDESK',font=('Segoe UI',17,'bold'),fg='#56d6bc',bg='#101827').pack(side='left',padx=12)
        tk.Label(top,text='Medical Store | Inventory & Billing',font=('Segoe UI',10),fg='#d3ddeb',bg='#101827').pack(side='left')
        tk.Label(top,text=date.today().strftime('%d %b %Y')+'  ',font=('Segoe UI',10),fg='white',bg='#101827').pack(side='right')
        self.tabs=ttk.Notebook(self); self.tabs.pack(fill='both',expand=True,padx=14,pady=14)
        self.inv=ttk.Frame(self.tabs,padding=14); self.billing=ttk.Frame(self.tabs,padding=14)
        self.tabs.add(self.inv,text='  Inventory  '); self.tabs.add(self.billing,text='  New Bill  ')
        self.build_inventory(); self.build_billing(); self.refresh_inventory()
    def table(self,parent,cols,widths):
        frame=ttk.Frame(parent); frame.pack(fill='both',expand=True)
        tree=ttk.Treeview(frame,columns=cols,show='headings')
        for c,w in zip(cols,widths): tree.heading(c,text=c); tree.column(c,width=w,anchor='w')
        sy=ttk.Scrollbar(frame,orient='vertical',command=tree.yview); sx=ttk.Scrollbar(frame,orient='horizontal',command=tree.xview); tree.configure(yscrollcommand=sy.set,xscrollcommand=sx.set)
        tree.grid(row=0,column=0,sticky='nsew'); sy.grid(row=0,column=1,sticky='ns'); sx.grid(row=1,column=0,sticky='ew'); frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
        return tree
    def build_inventory(self):
        tk.Label(self.inv,text='Medicine Inventory',font=('Segoe UI',18,'bold'),bg='#f2f5f9',fg='#182437').pack(anchor='w')
        tk.Label(self.inv,text='Search stock, batch, category or manufacturer. Prices and dates in starter data are examples.',font=('Segoe UI',9),bg='#f2f5f9',fg='#64748b').pack(anchor='w',pady=(3,12))
        bar=ttk.Frame(self.inv); bar.pack(fill='x',pady=(0,10)); self.search=ttk.Entry(bar); self.search.pack(side='left',fill='x',expand=True); self.search.insert(0,''); self.search.bind('<KeyRelease>',lambda e:self.refresh_inventory())
        ttk.Button(bar,text='Refresh',command=self.refresh_inventory).pack(side='left',padx=8)
        cols=('ID','Medicine','Form','Category','Manufacturer','Batch','Price ₹','Expiry','Stock','Reorder','Rx / note','Storage')
        self.inv_tree=self.table(self.inv,cols,(45,190,105,165,125,85,75,90,60,65,230,150))
        self.inv_tree.tag_configure('low',background='#fff2df'); self.inv_tree.tag_configure('expired',background='#ffe5e5')
        ttk.Label(self.inv,text='Amber = low stock   •   Red = expired',foreground='#64748b').pack(anchor='w',pady=6)
    def refresh_inventory(self):
        if not hasattr(self,'inv_tree'): return
        self.inv_tree.delete(*self.inv_tree.get_children()); q=self.search.get().strip().lower() if hasattr(self,'search') else ''
        rows=self.db.db.execute('SELECT * FROM medicines ORDER BY name').fetchall()
        for r in rows:
            if q and not q in ' '.join(str(r[k]) for k in ['name','form','category','manufacturer','batch','barcode']).lower(): continue
            tag='expired' if r['expiry'] < date.today().isoformat() else ('low' if r['stock'] <= r['reorder_level'] else '')
            self.inv_tree.insert('', 'end', values=(r['id'],r['name'],r['form'],r['category'],r['manufacturer'],r['batch'],f"{r['price']:.2f}",r['expiry'],r['stock'],r['reorder_level'],r['prescription'],r['storage']),tags=(tag,))
    def build_billing(self):
        tk.Label(self.billing,text='Create Customer Bill',font=('Segoe UI',18,'bold'),bg='#f2f5f9',fg='#182437').pack(anchor='w')
        tk.Label(self.billing,text='Select an in-stock, unexpired item from inventory and add its quantity.',font=('Segoe UI',9),bg='#f2f5f9',fg='#64748b').pack(anchor='w',pady=(3,12))
        customer=ttk.Frame(self.billing); customer.pack(fill='x',pady=(0,12))
        ttk.Label(customer,text='Customer name').grid(row=0,column=0,sticky='w'); self.customer=ttk.Entry(customer,width=32); self.customer.grid(row=1,column=0,padx=(0,12),pady=4)
        ttk.Label(customer,text='Phone (optional)').grid(row=0,column=1,sticky='w'); self.phone=ttk.Entry(customer,width=24); self.phone.grid(row=1,column=1,padx=(0,12),pady=4)
        ttk.Label(customer,text='Medicine').grid(row=0,column=2,sticky='w'); self.med_combo=ttk.Combobox(customer,state='readonly',width=48); self.med_combo.grid(row=1,column=2,padx=(0,12),pady=4)
        ttk.Label(customer,text='Qty').grid(row=0,column=3,sticky='w'); self.qty=ttk.Spinbox(customer,from_=1,to=999,width=7); self.qty.grid(row=1,column=3,pady=4); self.qty.set(1)
        ttk.Button(customer,text='Add item',command=self.add_item).grid(row=1,column=4,padx=10)
        customer.columnconfigure(2,weight=1); self.load_combo()
        self.cart_tree=self.table(self.billing,('ID','Medicine','Batch','Expiry','Qty','Unit ₹','Amount ₹'),(60,350,110,100,80,100,120))
        bottom=ttk.Frame(self.billing); bottom.pack(fill='x',pady=12)
        ttk.Button(bottom,text='Remove selected',command=self.remove_item).pack(side='left'); ttk.Button(bottom,text='Clear bill',command=self.clear_cart).pack(side='left',padx=8)
        self.total_lbl=ttk.Label(bottom,text='Total: ₹0.00',font=('Segoe UI',16,'bold')); self.total_lbl.pack(side='right',padx=12)
        ttk.Button(bottom,text='Save & Generate Invoice',command=self.checkout).pack(side='right',ipadx=12,ipady=6)
        ttk.Label(self.billing,text='Invoice is saved as a text file in the invoices folder; a sales record is also kept in the local database.',foreground='#64748b').pack(anchor='w')
    def load_combo(self):
        self.meds=self.db.db.execute('SELECT * FROM medicines ORDER BY name').fetchall()
        self.med_combo['values']=[f"{r['id']} | {r['name']} | ₹{r['price']:.2f} | stock {r['stock']}" for r in self.meds]
        if self.meds and not self.med_combo.get(): self.med_combo.current(0)
    def add_item(self):
        i=self.med_combo.current()
        if i<0: messagebox.showwarning('Select medicine','Choose a medicine.'); return
        r=self.meds[i]; qty=int(self.qty.get())
        if r['expiry'] < date.today().isoformat(): messagebox.showerror('Expired','Expired stock cannot be added to a bill.'); return
        already=self.cart.get(r['id'],{}).get('qty',0)
        if qty<1 or already+qty>r['stock']: messagebox.showerror('Stock unavailable',f"Available quantity: {r['stock']-already}"); return
        self.cart[r['id']]={'row':r,'qty':already+qty}; self.render_cart()
    def render_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children()); total=0
        for mid,item in self.cart.items():
            r=item['row']; q=item['qty']; amount=q*r['price']; total+=amount
            self.cart_tree.insert('', 'end', iid=str(mid), values=(mid,r['name'],r['batch'],r['expiry'],q,f"{r['price']:.2f}",f"{amount:.2f}"))
        self.total_lbl.config(text=f'Total: ₹{total:.2f}')
    def remove_item(self):
        sel=self.cart_tree.selection()
        if sel: self.cart.pop(int(sel[0]),None); self.render_cart()
    def clear_cart(self): self.cart.clear(); self.render_cart()
    def checkout(self):
        if not self.cart: messagebox.showwarning('Empty bill','Add at least one item.'); return
        customer=self.customer.get().strip() or 'Walk-in customer'; phone=self.phone.get().strip()
        invoice='INV-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:20]; sold=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); total=sum(x['qty']*x['row']['price'] for x in self.cart.values())
        path=INVOICE_DIR/(invoice+'.txt')
        lines=['MEDIDESK MEDICAL STORE','Customer Bill',f'Invoice: {invoice}',f'Date: {sold}',f'Customer: {customer}',f'Phone: {phone or "-"}','-'*72,'Medicine | Batch | Expiry | Qty | Unit Price | Amount','-'*72]
        for item in self.cart.values():
            r=item['row']; q=item['qty']; lines.append(f"{r['name']} | {r['batch']} | {r['expiry']} | {q} | Rs {r['price']:.2f} | Rs {q*r['price']:.2f}")
        lines += ['-'*72,f'TOTAL: Rs {total:.2f}','Thank you. Please retain this invoice.']
        try:
            with self.db.db:
                for mid,item in self.cart.items():
                    stock=self.db.db.execute('SELECT stock,expiry,price,name,batch FROM medicines WHERE id=?',(mid,)).fetchone()
                    if not stock or stock['stock'] < item['qty'] or stock['expiry'] < date.today().isoformat(): raise ValueError(f"Stock/expiry changed for {item['row']['name']}; refresh inventory and retry.")
                path.write_text('\n'.join(lines),encoding='utf-8')
                self.db.db.execute('INSERT INTO sales VALUES(?,?,?,?,?,?)',(invoice,sold,customer,phone,total,str(path)))
                for mid,item in self.cart.items():
                    r=item['row']; q=item['qty']; self.db.db.execute('UPDATE medicines SET stock=stock-? WHERE id=?',(q,mid))
                    self.db.db.execute('INSERT INTO sale_items(invoice,medicine_id,name,qty,unit_price,line_total) VALUES(?,?,?,?,?,?)',(invoice,mid,r['name'],q,r['price'],q*r['price']))
        except Exception as e:
            if path.exists(): path.unlink()
            messagebox.showerror('Could not save invoice',str(e)); return
        messagebox.showinfo('Invoice saved',f'Invoice saved:\n{path}\n\nTotal: ₹{total:.2f}')
        self.cart.clear(); self.render_cart(); self.load_combo(); self.refresh_inventory()

if __name__=='__main__': Login().mainloop()
