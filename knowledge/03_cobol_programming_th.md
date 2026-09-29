# การเขียนโปรแกรมภาษาโคบอล (COBOL Programming): ตัวแปร เงื่อนไข การทำซ้ำ และฟังก์ชัน

## 1. ภาพรวมภาษาโคบอลและเหตุผลที่ยังมีชีวิตอยู่

**โคบอล (COBOL — Common Business-Oriented Language)** ถือกำเนิดในปี ค.ศ. 1959 จากคณะกรรมการ CODASYL (Conference on Data Systems Languages) โดยมี Grace Hopper เป็นผู้มีอิทธิพลทางความคิดสำคัญ เป้าหมายการออกแบบคือให้ **ผู้บริหารและนักบัญชีอ่านโค้ดรู้เรื่อง** จึงใช้ไวยากรณ์ (syntax) ที่เหมือนภาษาอังกฤษ เช่น `ADD 1 TO WS-COUNTER` แทนที่จะเขียน `counter++` ผลคือโปรแกรมโคบอลยาวกว่าภาษาสมัยใหม่มาก แต่ **อ่านง่ายและบำรุงรักษาได้นานหลายสิบปี** ซึ่งกลายเป็นคุณสมบัติที่มีค่าที่สุดในระบบที่ต้องอยู่ยาว

ปัจจุบันโคบอลยังคงรันอยู่ในระบบหลักของธนาคาร บริษัทประกัน ระบบบัตรเครดิต ระบบสวัสดิการรัฐ และสายการบิน เหตุผลหลักไม่ใช่แค่ "ย้ายออกยาก" แต่มีเหตุผลทางเทคนิคที่แข็งแรงสามข้อ ข้อแรกคือ **เลขทศนิยมฐานสิบ (decimal arithmetic)** โคบอลคำนวณด้วยฐานสิบโดยตรงผ่านชนิดข้อมูล **แพ็กเดซิมอล (packed decimal / COMP-3)** ต่างจากภาษาสมัยใหม่ที่มักใช้ **เลขทศนิยมฐานสอง (binary floating point)** ซึ่งไม่สามารถแทนค่า 0.1 ได้อย่างแม่นยำ ในงานการเงินที่ต้องกระทบยอดถึงหน่วยสตางค์ ความแตกต่างนี้สำคัญมาก ข้อที่สองคือ **ประสิทธิภาพในการประมวลผลแบบกลุ่ม (batch processing)** บนเครื่องเมนเฟรม (mainframe) ที่สามารถอ่านและเขียนไฟล์ระเบียนหลักร้อยล้านรายการต่อคืนได้ ข้อที่สามคือ **ความเสถียรของมาตรฐาน** โค้ดที่เขียนตามมาตรฐาน COBOL-85 ยังคอมไพล์ผ่านบนคอมไพเลอร์ปัจจุบันได้เป็นส่วนใหญ่ ตัวอย่างคอมไพเลอร์ที่ใช้ทดสอบโค้ดในเอกสารนี้คือ **GnuCOBOL** ซึ่งเป็นซอฟต์แวร์เสรีที่แปลงโคบอลเป็นภาษาซี (C) แล้วคอมไพล์ต่อ

## 2. โครงสร้าง 4 ดิวิชัน (Division)

โปรแกรมโคบอลทุกโปรแกรมมีลำดับชั้นที่ตายตัวคือ **ดิวิชัน (division) → เซกชัน (section) → พารากราฟ (paragraph) → ประโยคคำสั่ง (sentence) → คำสั่ง (statement)** และมีดิวิชันหลักสี่ตัวที่ต้องเรียงตามลำดับนี้เสมอ

| ดิวิชัน | บังคับหรือไม่ | หน้าที่ | เซกชันที่พบบ่อย |
|---|---|---|---|
| `IDENTIFICATION DIVISION` | บังคับ | ระบุชื่อโปรแกรมและข้อมูลผู้เขียน มีเพียง `PROGRAM-ID` ที่บังคับจริง | — |
| `ENVIRONMENT DIVISION` | ไม่บังคับ | เชื่อมโปรแกรมกับสภาพแวดล้อมของเครื่อง เช่น จับคู่ชื่อไฟล์เชิงตรรกะกับไฟล์จริง | `CONFIGURATION SECTION`, `INPUT-OUTPUT SECTION` |
| `DATA DIVISION` | ไม่บังคับ | ประกาศตัวแปร (variable) และโครงสร้างระเบียน (record) ทั้งหมด | `FILE SECTION`, `WORKING-STORAGE SECTION`, `LOCAL-STORAGE SECTION`, `LINKAGE SECTION` |
| `PROCEDURE DIVISION` | บังคับในทางปฏิบัติ | ตรรกะการทำงานทั้งหมด | ผู้เขียนกำหนดเซกชันเอง |

จุดที่สำคัญเชิงแนวคิดคือ **โคบอลแยกการประกาศข้อมูลออกจากตรรกะโดยเด็ดขาด** ไม่มีการประกาศตัวแปรกลางฟังก์ชันแบบภาษาสมัยใหม่ ตัวแปรทุกตัวต้องอยู่ใน `DATA DIVISION` ทำให้ผู้อ่านเห็นโครงสร้างข้อมูลทั้งหมดในที่เดียว ซึ่งสอดคล้องกับคำกล่าวว่า "ถ้าคุณเข้าใจ DATA DIVISION คุณเข้าใจโปรแกรมไปแล้วครึ่งหนึ่ง"

**รูปแบบคอลัมน์ (fixed format)** ในโคบอลดั้งเดิม บรรทัดโค้ดถูกแบ่งเป็นเขตตายตัว ได้แก่ คอลัมน์ 1–6 เป็นเลขลำดับ (sequence number), คอลัมน์ 7 เป็นตัวบ่งชี้ (indicator area) ใช้ `*` สำหรับหมายเหตุ (comment) และ `-` สำหรับต่อสายอักขระ, คอลัมน์ 8–11 คือ **แอเรียเอ (Area A)** ใช้เขียนชื่อดิวิชัน ชื่อเซกชัน ชื่อพารากราฟ และระดับหมายเลข 01 กับ 77, คอลัมน์ 12–72 คือ **แอเรียบี (Area B)** ใช้เขียนคำสั่งทั่วไป และคอลัมน์ 73–80 สงวนไว้สำหรับรหัสระบุโปรแกรม คอมไพเลอร์สมัยใหม่รองรับ **รูปแบบอิสระ (free format)** ที่ไม่บังคับคอลัมน์ แต่โค้ดในระบบจริงส่วนใหญ่ยังเป็นรูปแบบคอลัมน์

## 3. กฎการตั้งชื่อตัวแปร (Data Name / Identifier)

กฎการตั้งชื่อ **ชื่อข้อมูล (data name)** ในโคบอลมีดังนี้ หนึ่ง ความยาวไม่เกิน **30 ตัวอักษร** สอง ใช้ได้เฉพาะตัวอักษร A–Z (ไม่แยกตัวพิมพ์ใหญ่เล็ก), ตัวเลข 0–9 และ **เครื่องหมายยัติภังค์ (hyphen)** เท่านั้น ห้ามใช้ขีดล่าง (underscore) หรือช่องว่าง สาม **ห้ามขึ้นต้นหรือลงท้ายด้วยยัติภังค์** และห้ามมียัติภังค์สองตัวติดกัน สี่ ต้องมีตัวอักษรอย่างน้อยหนึ่งตัว ชื่อที่เป็นตัวเลขล้วนจะถูกตีความเป็นค่าคงที่ ห้า **ห้ามใช้คำสงวน (reserved word)** ซึ่งในมาตรฐาน COBOL-85 มีประมาณ 300 คำ และในภาษาถิ่น (dialect) บางตัวมีมากกว่า 500 คำ เช่น `DATE`, `TIME`, `COUNT`, `LENGTH`, `STATUS`, `NUMBER`, `DAY`, `KEY`, `SUM`, `TOTAL` ล้วนเป็นคำสงวนที่มือใหม่มักเผลอใช้

| ชื่อที่เขียน | ถูกต้องหรือไม่ | เหตุผล |
|---|---|---|
| `WS-CUSTOMER-NAME` | ถูก | ตัวอักษร ตัวเลข ยัติภังค์ ครบตามกฎ |
| `WS-TOTAL-AMOUNT-2026` | ถูก | ตัวเลขอยู่ท้ายได้ |
| `1ST-CUSTOMER` | ถูก | ขึ้นต้นด้วยตัวเลขได้ ตราบใดที่มีตัวอักษรอยู่ด้วย |
| `-WS-AMOUNT` | ผิด | ขึ้นต้นด้วยยัติภังค์ |
| `WS-AMOUNT-` | ผิด | ลงท้ายด้วยยัติภังค์ |
| `WS_AMOUNT` | ผิด | ใช้ขีดล่าง (underscore) ไม่ได้ |
| `TOTAL` | ผิด | เป็นคำสงวน (reserved word) |
| `WS-CUSTOMER-ACCOUNT-BALANCE-AMT` | ผิด | ยาว 31 ตัวอักษร เกิน 30 |
| `12345` | ผิด | ไม่มีตัวอักษรเลย |

ในทางปฏิบัติ ทีมพัฒนามักใช้ **ธรรมเนียมการตั้งคำนำหน้า (prefix convention)** เพื่อบอกที่มาของตัวแปรทันทีที่เห็น เช่น `WS-` สำหรับ `WORKING-STORAGE SECTION`, `LS-` สำหรับ `LINKAGE SECTION`, `FD-` หรือ `IN-`/`OUT-` สำหรับระเบียนไฟล์ และ `SW-` หรือ `FL-` สำหรับตัวแปรธง (flag/switch) ธรรมเนียมนี้ไม่ใช่กฎของภาษา แต่ช่วยลดข้อผิดพลาดอย่างมากในโปรแกรมที่มีตัวแปรหลายร้อยตัว

## 4. การประกาศตัวแปร: ระดับหมายเลขและ PICTURE Clause

**ระดับหมายเลข (level number)** เป็นตัวเลขสองหลักที่นำหน้าชื่อตัวแปร ใช้บอกลำดับชั้นของโครงสร้างข้อมูล ระดับ **01** คือระดับบนสุดของระเบียน (record) ระดับ **02–49** คือระดับย่อยลงไป ยิ่งเลขมากยิ่งอยู่ลึก โดยธรรมเนียมมักเว้นทีละ 5 (01, 05, 10, 15) เพื่อให้แทรกระดับใหม่ได้ภายหลัง ระดับ **77** ใช้ประกาศตัวแปรเดี่ยวที่ไม่มีโครงสร้างย่อย ซึ่งถือว่าล้าสมัยแล้วและควรใช้ 01 แทน ระดับ **88** ใช้ประกาศ **ชื่อเงื่อนไข (condition name)** ซึ่งจะอธิบายในหัวข้อ 5 ระดับ **66** ใช้กับ `RENAMES` ซึ่งพบน้อยมาก

ตัวแปรที่มีระดับย่อยอยู่ข้างใต้เรียกว่า **กลุ่มข้อมูล (group item)** และจะไม่มี `PICTURE clause` ของตัวเอง โคบอลถือว่ากลุ่มข้อมูลเป็นสายอักขระ (alphanumeric) เสมอ ส่วนตัวแปรที่ไม่มีระดับย่อยเรียกว่า **ข้อมูลมูลฐาน (elementary item)** และ **ต้องมี PICTURE clause เสมอ** ยกเว้นกรณีที่ประกาศ `USAGE` แบบทศนิยมลอยตัว

**PICTURE clause** (เขียนย่อว่า `PIC`) กำหนดชนิดและขนาดของข้อมูล สัญลักษณ์หลักมีดังตาราง

| สัญลักษณ์ | ความหมาย | ตัวอย่าง | ขนาด (ไบต์, USAGE DISPLAY) | ค่าที่เก็บได้ |
|---|---|---|---|---|
| `9` | ตัวเลข (numeric) หนึ่งหลัก | `PIC 9(5)` | 5 | 00000 ถึง 99999 |
| `X` | อักขระใดก็ได้ (alphanumeric) | `PIC X(20)` | 20 | ข้อความยาว 20 ตัวอักษร |
| `A` | ตัวอักษรหรือช่องว่างเท่านั้น (alphabetic) | `PIC A(10)` | 10 | ตัวอักษร A–Z และเว้นวรรค |
| `S` | มีเครื่องหมาย (sign) — ไม่กินเนื้อที่เพิ่มเมื่อใช้ SIGN IS INCLUDED | `PIC S9(5)` | 5 | −99999 ถึง +99999 |
| `V` | จุดทศนิยมสมมติ (implied decimal point) — ไม่กินเนื้อที่ | `PIC 9(7)V99` | 9 | 0000000.00 ถึง 9999999.99 |
| `P` | ตัวคูณกำลังสิบ (scaling position) | `PIC 9(3)PPP` | 3 | จำนวนเต็มพันเท่า |
| `Z` | ระงับเลขศูนย์นำหน้า (zero suppression) — ใช้กับตัวแปรแสดงผล | `PIC ZZ,ZZ9.99` | 9 | แสดง `   1,234.50` |
| `,` `.` `-` `+` `$` `*` `CR` `DB` | อักขระตกแต่ง (editing character) สำหรับรายงาน | `PIC $$$,$$9.99` | 10 | แสดง `   $1,234.50` |

ตัวอย่างที่สำคัญที่สุดคือความต่างระหว่าง **จุดทศนิยมสมมติ (V)** กับ **จุดทศนิยมจริง (.)** ตัวแปร `PIC 9(5)V99` กินพื้นที่ 7 ไบต์และเก็บค่าตัวเลขจริงที่นำไปคำนวณได้ ส่วน `PIC 9(5).99` กินพื้นที่ 8 ไบต์เพราะจุดถูกเก็บเป็นอักขระจริง และถือเป็น **ตัวแปรแสดงผล (edited field)** ที่ **ห้ามนำไปคำนวณ** ซึ่งเป็นข้อผิดพลาดยอดฮิตของมือใหม่

**USAGE clause** กำหนดรูปแบบการเก็บภายในหน่วยความจำ ค่าปริยาย (default) คือ `DISPLAY` ซึ่งเก็บหนึ่งหลักต่อหนึ่งไบต์ อ่านง่ายแต่เปลืองพื้นที่และคำนวณช้า `COMP` หรือ `BINARY` เก็บเป็นเลขฐานสองแบบเต็มจำนวน คำนวณเร็วที่สุดสำหรับตัวนับ (counter) และดัชนี (index) ส่วน `COMP-3` หรือ `PACKED-DECIMAL` เก็บสองหลักต่อหนึ่งไบต์ โดยครึ่งไบต์สุดท้ายเก็บเครื่องหมาย ทำให้ใช้พื้นที่ **⌈(จำนวนหลัก + 1) ÷ 2⌉ ไบต์** และยังคงความแม่นยำฐานสิบไว้ครบ จึงเป็นชนิดข้อมูลมาตรฐานของงานการเงิน

| การประกาศ | จำนวนหลัก | USAGE | ขนาดจริง | ใช้เมื่อใด |
|---|---|---|---|---|
| `PIC S9(7)V99` | 9 | DISPLAY | 9 ไบต์ | ต้องการอ่านค่าดิบในไฟล์ได้ด้วยตา |
| `PIC S9(7)V99 COMP-3` | 9 | PACKED-DECIMAL | ⌈10÷2⌉ = 5 ไบต์ | ยอดเงินในฐานข้อมูล ประหยัด 44% |
| `PIC S9(4) COMP` | 4 | BINARY | 2 ไบต์ | ตัวนับในลูป ดัชนีตาราง |
| `PIC S9(9) COMP` | 9 | BINARY | 4 ไบต์ | จำนวนระเบียนที่ประมวลผล |

## 5. คำสั่งเงื่อนไข (Conditional Statement)

รูปแบบพื้นฐานคือ `IF ... ELSE ... END-IF` โดย **`END-IF` เป็นตัวปิดขอบเขต (scope terminator)** ที่เพิ่มเข้ามาใน COBOL-85 และควรใช้เสมอ เพราะโค้ดรุ่นเก่าที่จบเงื่อนไขด้วยจุด (period) ทำให้เกิดข้อผิดพลาดยากตรวจสอบ เมื่อมีคนเผลอใส่จุดกลางบล็อก

```cobol
       IF  WS-BALANCE > 100000
           MOVE "PLATINUM" TO WS-TIER
       ELSE
           IF  WS-BALANCE > 50000
               MOVE "GOLD"   TO WS-TIER
           ELSE
               MOVE "SILVER" TO WS-TIER
           END-IF
       END-IF.
```

โคบอลรองรับเงื่อนไขสี่ตระกูล **เงื่อนไขเชิงเปรียบเทียบ (relational condition)** ใช้ `>`, `<`, `=`, `>=`, `<=`, `NOT =` หรือเขียนเป็นคำว่า `GREATER THAN`, `LESS THAN`, `EQUAL TO` **เงื่อนไขเชิงชนิด (class condition)** ตรวจว่าเนื้อหาของตัวแปรเป็นชนิดใด ได้แก่ `IS NUMERIC`, `IS ALPHABETIC`, `IS ALPHABETIC-UPPER`, `IS ALPHABETIC-LOWER` ซึ่งมีประโยชน์มากในการตรวจสอบความถูกต้องของข้อมูลนำเข้า (input validation) เช่น `IF WS-INPUT-AGE IS NOT NUMERIC` **เงื่อนไขเชิงเครื่องหมาย (sign condition)** ใช้ `IS POSITIVE`, `IS NEGATIVE`, `IS ZERO` และ **เงื่อนไขผสม (compound condition)** ใช้ `AND`, `OR`, `NOT` โดยลำดับความสำคัญคือ `NOT` มาก่อน `AND` และ `AND` มาก่อน `OR`

**ชื่อเงื่อนไขระดับ 88 (condition name)** เป็นคุณสมบัติเด่นที่ทำให้โค้ดโคบอลอ่านเหมือนภาษาอังกฤษจริง ๆ โดยผูกชื่อเชิงความหมายเข้ากับค่าของตัวแปรแม่

```cobol
       01  WS-ACCOUNT-STATUS      PIC X(1) VALUE "A".
           88  ACCOUNT-ACTIVE                VALUE "A".
           88  ACCOUNT-DORMANT               VALUE "D".
           88  ACCOUNT-CLOSED                VALUE "C" "X".
           88  ACCOUNT-USABLE                VALUE "A" "D".
       01  WS-EOF-FLAG            PIC X(1) VALUE "N".
           88  END-OF-FILE                   VALUE "Y".
           88  NOT-END-OF-FILE               VALUE "N".
```

จากการประกาศข้างต้น สามารถเขียน `IF ACCOUNT-ACTIVE` แทน `IF WS-ACCOUNT-STATUS = "A"` ได้ทันที และเมื่อกฎธุรกิจเปลี่ยน เช่น เพิ่มรหัส `"X"` ให้หมายถึงปิดบัญชีด้วย ก็แก้ที่จุดประกาศเพียงจุดเดียว ไม่ต้องไล่แก้ทุกที่ในโปรแกรม นอกจากนี้ยังใช้ `SET ACCOUNT-CLOSED TO TRUE` เพื่อกำหนดค่าย้อนกลับได้ ซึ่งจะใส่ค่าแรกในรายการ VALUE คือ `"C"` ให้ตัวแปรแม่

**คำสั่ง EVALUATE** ทำหน้าที่คล้าย `switch` ในภาษาซี แต่ยืดหยุ่นกว่ามาก รูปแบบที่ใช้บ่อยที่สุดคือ `EVALUATE TRUE` ซึ่งเปลี่ยนให้แต่ละ `WHEN` เป็นเงื่อนไขเต็มรูปแบบ ทำให้แทนที่ `IF` ซ้อนกันหลายชั้นได้อย่างสะอาด และ **ไม่มีปัญหาตกทะลุ (fall-through)** แบบภาษาซี เพราะโคบอลออกจากบล็อกทันทีเมื่อ `WHEN` แรกที่เป็นจริงทำงานเสร็จ

```cobol
       EVALUATE TRUE
           WHEN WS-PURCHASE >= 100000    MOVE 15 TO WS-DISCOUNT-PCT
           WHEN WS-PURCHASE >=  50000    MOVE 10 TO WS-DISCOUNT-PCT
           WHEN WS-PURCHASE >=  10000    MOVE  5 TO WS-DISCOUNT-PCT
           WHEN OTHER                    MOVE  0 TO WS-DISCOUNT-PCT
       END-EVALUATE.
```

รูปแบบอื่นได้แก่ `EVALUATE WS-GRADE WHEN "A" ... WHEN "B" ...` สำหรับเทียบค่าตรง ๆ, `WHEN 1 THRU 10` สำหรับช่วงค่า และ `EVALUATE WS-A ALSO WS-B` สำหรับเทียบสองตัวแปรพร้อมกันในลักษณะตารางตัดสินใจ (decision table)

## 6. คำสั่งทำซ้ำ (PERFORM)

โคบอลไม่มีคำสั่ง `for` หรือ `while` แยกกัน แต่รวมทุกรูปแบบของการวนซ้ำ (loop) และการเรียกซับรูทีนไว้ในคำสั่งเดียวคือ `PERFORM` ตารางต่อไปนี้สรุปรูปแบบทั้งหมด

| รูปแบบ | ไวยากรณ์ | เทียบกับภาษาสมัยใหม่ | หมายเหตุ |
|---|---|---|---|
| เรียกพารากราฟ | `PERFORM 200-PROCESS-REC` | เรียกฟังก์ชันหนึ่งครั้ง | เป็นรากฐานของการเขียนแบบมีโครงสร้าง |
| ทำซ้ำ n ครั้ง | `PERFORM 200-PROC N TIMES` | `for i in range(n)` | `N` ต้องเป็นตัวแปรตัวเลขหรือค่าคงที่ |
| ทำจนกว่าเงื่อนไขจริง | `PERFORM 200-PROC UNTIL END-OF-FILE` | `while not eof` | ตรวจเงื่อนไข **ก่อน** ทำงาน (pre-test) |
| ทดสอบทีหลัง | `PERFORM 200-PROC WITH TEST AFTER UNTIL WS-I > 5` | `do ... while` | ทำงานอย่างน้อยหนึ่งรอบเสมอ |
| ทำซ้ำพร้อมนับ | `PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > 10` | `for i = 1 to 10` | เพิ่มค่าให้อัตโนมัติหลังจบรอบ |
| ซ้อนสองมิติ | `PERFORM VARYING WS-I ... AFTER WS-J FROM 1 BY 1 UNTIL WS-J > 5` | ลูปซ้อน (nested loop) | `AFTER` คือลูปชั้นใน วนเร็วกว่า |
| ช่วงพารากราฟ | `PERFORM 200-START THRU 200-EXIT` | เรียกกลุ่มพารากราฟติดกัน | เสี่ยงต่อการบำรุงรักษา ควรหลีกเลี่ยง |
| แบบฝังในบรรทัด | `PERFORM UNTIL ... ... END-PERFORM` | บล็อกลูปแบบปกติ | เรียก **inline PERFORM** |

ความต่างที่ต้องเข้าใจให้ชัดคือ **แบบนอกบรรทัด (out-of-line PERFORM)** จะเรียกไปยังพารากราฟที่เขียนแยกไว้ที่อื่น ทำให้ตรรกะหลักสั้นและอ่านง่าย แต่ผู้อ่านต้องกระโดดไปดูพารากราฟนั้น ส่วน **แบบฝังในบรรทัด (inline PERFORM)** ซึ่งจบด้วย `END-PERFORM` เก็บตรรกะไว้ในที่เดียว เหมาะกับลูปสั้น ๆ ไม่เกิน 10–15 บรรทัด สำหรับ `PERFORM VARYING` มีจุดสำคัญที่มักเข้าใจผิด คือ **ค่าของตัวแปรควบคุมเมื่อออกจากลูปจะเกินขอบเขตไปหนึ่งก้าวเสมอ** เช่น `PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > 10` เมื่อจบลูป `WS-I` มีค่าเท่ากับ 11 ไม่ใช่ 10 และลำดับการทำงานคือ กำหนดค่าเริ่มต้น → ตรวจเงื่อนไข → ทำงาน → เพิ่มค่า → กลับไปตรวจเงื่อนไข ส่วน `PERFORM THRU` นั้นควรหลีกเลี่ยงเพราะถ้ามีคนแทรกพารากราฟใหม่ระหว่างจุดเริ่มและจุดจบ พารากราฟนั้นจะถูกเรียกโดยไม่ตั้งใจ

## 7. ฟังก์ชัน (Function) และการเรียกโปรแกรมย่อย

**ฟังก์ชันในตัว (intrinsic function)** ถูกเพิ่มเข้ามาในมาตรฐาน COBOL-89/2002 เรียกใช้ด้วยคำสำคัญ `FUNCTION` นำหน้าเสมอ

| ฟังก์ชัน | หน้าที่ | ตัวอย่างการใช้ | ผลลัพธ์ |
|---|---|---|---|
| `FUNCTION LENGTH(x)` | คืนความยาวของตัวแปรเป็นไบต์ | `FUNCTION LENGTH(WS-NAME)` เมื่อ `WS-NAME PIC X(20)` | 20 |
| `FUNCTION NUMVAL(x)` | แปลงสายอักขระเป็นตัวเลข | `FUNCTION NUMVAL(" -12.75 ")` | −12.75 |
| `FUNCTION NUMVAL-C(x)` | แปลงสายอักขระที่มีสัญลักษณ์สกุลเงินและจุลภาค | `FUNCTION NUMVAL-C("$1,234.56")` | 1234.56 |
| `FUNCTION CURRENT-DATE` | คืนวันเวลาปัจจุบันเป็นสายอักขระ 21 ตัวอักษร | รูปแบบ `YYYYMMDDHHMMSSss±hhmm` | `20260725093015420700` + offset |
| `FUNCTION MAX(a b c)` | ค่ามากที่สุดในรายการ | `FUNCTION MAX(12 45 7)` | 45 |
| `FUNCTION MIN(a b c)` | ค่าน้อยที่สุดในรายการ | `FUNCTION MIN(12 45 7)` | 7 |
| `FUNCTION MOD(a b)` | เศษเหลือ (ผลลัพธ์มีเครื่องหมายตามตัวหาร) | `FUNCTION MOD(-7 3)` | 2 |
| `FUNCTION REM(a b)` | เศษเหลือ (ผลลัพธ์มีเครื่องหมายตามตัวตั้ง) | `FUNCTION REM(-7 3)` | −1 |
| `FUNCTION INTEGER(x)` | จำนวนเต็มที่ไม่เกินค่าที่ให้ (floor) | `FUNCTION INTEGER(-2.3)` | −3 |
| `FUNCTION UPPER-CASE(x)` | แปลงเป็นตัวพิมพ์ใหญ่ | `FUNCTION UPPER-CASE("abc")` | `ABC` |

**สายอักขระที่ `FUNCTION CURRENT-DATE` คืนมา** มีโครงสร้างชัดเจนคือ ตำแหน่ง 1–4 ปี ค.ศ., 5–6 เดือน, 7–8 วัน, 9–10 ชั่วโมง, 11–12 นาที, 13–14 วินาที, 15–16 เศษหนึ่งส่วนร้อยของวินาที และ 17–21 คือส่วนต่างจากเวลามาตรฐานกรีนิช (GMT offset) เช่น `+0700` สำหรับเวลาประเทศไทย จึงต้องใช้ `MOVE WS-DATE-STR(1:8) TO WS-YYYYMMDD` เพื่อดึงเฉพาะส่วนที่ต้องการด้วย **การอ้างอิงช่วง (reference modification)** ในรูป `ตัวแปร(ตำแหน่งเริ่ม:ความยาว)`

**การเรียกโปรแกรมย่อย (subprogram)** ใช้คำสั่ง `CALL ... USING` โดยโปรแกรมย่อยต้องประกาศพารามิเตอร์ไว้ใน **`LINKAGE SECTION`** และรับเข้ามาผ่าน `PROCEDURE DIVISION USING` วิธีการส่งค่ามีสามแบบ **`BY REFERENCE`** เป็นค่าปริยาย ส่งที่อยู่หน่วยความจำไปตรง ๆ ทำให้โปรแกรมย่อยแก้ไขค่าแล้วสะท้อนกลับมายังโปรแกรมหลักได้ **`BY CONTENT`** คัดลอกค่าไปให้ โปรแกรมย่อยแก้ไขได้แต่ไม่กระทบต้นฉบับ เหมาะกับพารามิเตอร์นำเข้าที่ต้องการปกป้อง และ **`BY VALUE`** ส่งค่าจริงแบบภาษาซี ใช้เมื่อต้องเชื่อมกับโปรแกรมภาษาอื่น การจบโปรแกรมย่อยใช้ `GOBACK` ซึ่งปลอดภัยกว่า `EXIT PROGRAM` และ `STOP RUN` เพราะทำงานถูกต้องทั้งเมื่อเป็นโปรแกรมหลักและโปรแกรมย่อย

## 8. ตัวอย่างโปรแกรมสมบูรณ์

### 8.1 โปรแกรมคำนวณดอกเบี้ยเงินฝากทบต้น

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. DEPOSIT-INTEREST.
       AUTHOR. SELECTED-TOPICS-CLASS.
      *----------------------------------------------------------------
      * คำนวณดอกเบี้ยทบต้น (compound interest) รายปี แบบปัดเศษทุกสิ้นปี
      *----------------------------------------------------------------
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-INPUT-DATA.
           05  WS-PRINCIPAL      PIC 9(9)V99 VALUE 100000.00.
           05  WS-RATE-PCT       PIC 9(2)V99 VALUE 2.50.
           05  WS-YEARS          PIC 9(2)    VALUE 3.
       01  WS-WORK-AREA.
           05  WS-BALANCE        PIC 9(9)V99 VALUE ZERO.
           05  WS-INTEREST       PIC 9(9)V99 VALUE ZERO.
           05  WS-TOTAL-INT      PIC 9(9)V99 VALUE ZERO.
           05  WS-YEAR-NO        PIC 9(2)    VALUE ZERO.
       01  WS-REPORT-LINE.
           05  FILLER            PIC X(6)  VALUE "YEAR  ".
           05  WS-O-YEAR         PIC Z9.
           05  FILLER            PIC X(3)  VALUE "   ".
           05  FILLER            PIC X(10) VALUE "INTEREST= ".
           05  WS-O-INTEREST     PIC ZZZ,ZZ9.99.
           05  FILLER            PIC X(3)  VALUE "   ".
           05  FILLER            PIC X(9)  VALUE "BALANCE= ".
           05  WS-O-BALANCE      PIC Z,ZZZ,ZZ9.99.
       PROCEDURE DIVISION.
       000-MAIN.
           MOVE WS-PRINCIPAL TO WS-BALANCE
           DISPLAY "PRINCIPAL = " WS-PRINCIPAL
                   "  RATE = " WS-RATE-PCT "%  YEARS = " WS-YEARS
           PERFORM VARYING WS-YEAR-NO FROM 1 BY 1
                   UNTIL WS-YEAR-NO > WS-YEARS
               COMPUTE WS-INTEREST ROUNDED =
                       WS-BALANCE * WS-RATE-PCT / 100
               ADD WS-INTEREST TO WS-BALANCE
               ADD WS-INTEREST TO WS-TOTAL-INT
               MOVE WS-YEAR-NO  TO WS-O-YEAR
               MOVE WS-INTEREST TO WS-O-INTEREST
               MOVE WS-BALANCE  TO WS-O-BALANCE
               DISPLAY WS-REPORT-LINE
           END-PERFORM
           DISPLAY "TOTAL INTEREST EARNED = " WS-TOTAL-INT
           DISPLAY "LOOP COUNTER ENDS AT   = " WS-YEAR-NO
           GOBACK.
```

**ผลลัพธ์ที่คาดหวัง (expected output)** โดยยอดฝากตั้งต้น 100,000.00 บาท อัตราดอกเบี้ย 2.50% ต่อปี ระยะเวลา 3 ปี ทบต้นปีละครั้ง

```
PRINCIPAL = 100000.00  RATE = 02.50%  YEARS = 03
YEAR   1   INTEREST=   2,500.00   BALANCE=   102,500.00
YEAR   2   INTEREST=   2,562.50   BALANCE=   105,062.50
YEAR   3   INTEREST=   2,626.56   BALANCE=   107,689.06
TOTAL INTEREST EARNED = 000007689.06
LOOP COUNTER ENDS AT   = 04
```

จุดที่ควรสังเกตมีสามข้อ ข้อแรก ปีที่ 3 ดอกเบี้ยดิบคือ 105,062.50 × 0.025 = 2,626.5625 บาท และ `ROUNDED` ปัดเป็น 2,626.56 ถ้าไม่ใส่ `ROUNDED` โคบอลจะ **ตัดทิ้ง (truncate)** ได้ 2,626.56 เช่นกันในกรณีนี้ แต่ถ้าค่าเป็น 2,626.567 ผลจะต่างกันเป็น 2,626.57 กับ 2,626.56 ซึ่งในระบบที่ประมวลผลบัญชีนับล้าน ความต่างนี้สะสมเป็นเงินจำนวนมาก ข้อที่สอง `WS-YEAR-NO` มีค่า 04 เมื่อจบลูป ไม่ใช่ 03 ตามที่อธิบายในหัวข้อ 6 ข้อที่สาม `DISPLAY WS-TOTAL-INT` แสดงเลขศูนย์นำหน้าครบทุกหลักเป็น `000007689.06` เพราะเป็นตัวแปรตัวเลขดิบ ต่างจาก `WS-O-BALANCE` ที่ใช้ `PIC Z,ZZZ,ZZ9.99` จึงระงับศูนย์นำหน้าและใส่จุลภาคให้อัตโนมัติ

### 8.2 โปรแกรมประมวลผลรายการลูกค้าแบบวนซ้ำ

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CUSTOMER-DISCOUNT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-CUST-TABLE.
           05  FILLER PIC X(30) VALUE "SOMCHAI       000120000".
           05  FILLER PIC X(30) VALUE "SUDA          000075000".
           05  FILLER PIC X(30) VALUE "ANAN          000045000".
           05  FILLER PIC X(30) VALUE "MALEE         000008000".
           05  FILLER PIC X(30) VALUE "WICHAI        000010000".
       01  WS-CUST-LIST REDEFINES WS-CUST-TABLE.
           05  WS-CUST OCCURS 5 TIMES.
               10  WS-C-NAME     PIC X(14).
               10  WS-C-PURCHASE PIC 9(9).
               10  FILLER        PIC X(7).
       01  WS-COUNTERS.
           05  WS-IDX            PIC S9(4) COMP  VALUE ZERO.
           05  WS-DISC-PCT       PIC 9(2)        VALUE ZERO.
           05  WS-DISC-AMT       PIC 9(9)V99     VALUE ZERO.
           05  WS-NET            PIC 9(9)V99     VALUE ZERO.
           05  WS-TOT-GROSS      PIC 9(11)V99    VALUE ZERO.
           05  WS-TOT-DISC       PIC 9(11)V99    VALUE ZERO.
           05  WS-TOT-NET        PIC 9(11)V99    VALUE ZERO.
           05  WS-VIP-COUNT      PIC 9(3)        VALUE ZERO.
       01  WS-FLAGS.
           05  WS-TIER           PIC X(8)        VALUE SPACES.
               88  IS-VIP-TIER   VALUE "PLATINUM" "GOLD".
       PROCEDURE DIVISION.
       000-MAIN.
           DISPLAY "NAME            GROSS    PCT     DISCOUNT        NET"
           PERFORM VARYING WS-IDX FROM 1 BY 1 UNTIL WS-IDX > 5
               PERFORM 100-CLASSIFY
               PERFORM 200-COMPUTE
               PERFORM 300-PRINT
           END-PERFORM
           PERFORM 900-SUMMARY
           GOBACK.
       100-CLASSIFY.
           EVALUATE TRUE
               WHEN WS-C-PURCHASE(WS-IDX) >= 100000
                    MOVE 15 TO WS-DISC-PCT
                    MOVE "PLATINUM" TO WS-TIER
               WHEN WS-C-PURCHASE(WS-IDX) >=  50000
                    MOVE 10 TO WS-DISC-PCT
                    MOVE "GOLD"     TO WS-TIER
               WHEN WS-C-PURCHASE(WS-IDX) >=  10000
                    MOVE  5 TO WS-DISC-PCT
                    MOVE "SILVER"   TO WS-TIER
               WHEN OTHER
                    MOVE  0 TO WS-DISC-PCT
                    MOVE "BASIC"    TO WS-TIER
           END-EVALUATE
           IF IS-VIP-TIER
               ADD 1 TO WS-VIP-COUNT
           END-IF.
       200-COMPUTE.
           COMPUTE WS-DISC-AMT ROUNDED =
                   WS-C-PURCHASE(WS-IDX) * WS-DISC-PCT / 100
           COMPUTE WS-NET = WS-C-PURCHASE(WS-IDX) - WS-DISC-AMT
           ADD WS-C-PURCHASE(WS-IDX) TO WS-TOT-GROSS
           ADD WS-DISC-AMT           TO WS-TOT-DISC
           ADD WS-NET                TO WS-TOT-NET.
       300-PRINT.
           DISPLAY WS-C-NAME(WS-IDX) " " WS-C-PURCHASE(WS-IDX)
                   " " WS-DISC-PCT "% " WS-DISC-AMT " " WS-NET.
       900-SUMMARY.
           DISPLAY "RECORDS PROCESSED = " WS-IDX
           DISPLAY "VIP CUSTOMERS     = " WS-VIP-COUNT
           DISPLAY "TOTAL GROSS       = " WS-TOT-GROSS
           DISPLAY "TOTAL DISCOUNT    = " WS-TOT-DISC
           DISPLAY "TOTAL NET         = " WS-TOT-NET.
```

**ตารางผลลัพธ์ที่คาดหวัง** (แสดงเป็นตัวเลขที่อ่านง่ายเพื่อความชัดเจน)

| ลูกค้า | ยอดซื้อ (Gross) | ระดับ (Tier) | ส่วนลด % | ส่วนลด (บาท) | ยอดสุทธิ (Net) |
|---|---|---|---|---|---|
| SOMCHAI | 120,000 | PLATINUM | 15 | 18,000.00 | 102,000.00 |
| SUDA | 75,000 | GOLD | 10 | 7,500.00 | 67,500.00 |
| ANAN | 45,000 | SILVER | 5 | 2,250.00 | 42,750.00 |
| MALEE | 8,000 | BASIC | 0 | 0.00 | 8,000.00 |
| WICHAI | 10,000 | SILVER | 5 | 500.00 | 9,500.00 |
| **รวม** | **258,000** | — | — | **28,250.00** | **229,750.00** |

บรรทัดสรุปท้ายโปรแกรมจะแสดง `RECORDS PROCESSED = 0006` (เพราะ `WS-IDX` เกินไปหนึ่ง), `VIP CUSTOMERS = 002` (นับเฉพาะ PLATINUM กับ GOLD ตามชื่อเงื่อนไขระดับ 88), `TOTAL GROSS = 00000258000.00`, `TOTAL DISCOUNT = 00000028250.00` และ `TOTAL NET = 00000229750.00` โปรแกรมนี้แสดงเทคนิคสำคัญสามอย่างพร้อมกัน คือ **การประกาศตารางด้วย `OCCURS` และ `REDEFINES`** เพื่อสร้างข้อมูลทดสอบแบบฝังในโปรแกรม, **การแยกตรรกะเป็นพารากราฟย่อยแล้วเรียกด้วย out-of-line PERFORM** ซึ่งเป็นแบบแผนมาตรฐานของโคบอลเชิงโครงสร้าง และ **การใช้ชื่อเงื่อนไขระดับ 88 บนตัวแปรข้อความ** เพื่อรวมหลายค่าเป็นเงื่อนไขเดียว

### 8.3 การเรียกโปรแกรมย่อยด้วย CALL...USING

```cobol
      *>--- โปรแกรมหลัก ---
       IDENTIFICATION DIVISION.
       PROGRAM-ID. MAIN-VAT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-AMOUNT   PIC 9(7)V99 VALUE 1500.00.
       01  WS-RATE     PIC 9(2)V99 VALUE 7.00.
       01  WS-VAT      PIC 9(7)V99 VALUE ZERO.
       01  WS-TOTAL    PIC 9(7)V99 VALUE ZERO.
       PROCEDURE DIVISION.
           CALL "CALC-VAT" USING BY CONTENT   WS-AMOUNT
                                 BY CONTENT   WS-RATE
                                 BY REFERENCE WS-VAT
                                 BY REFERENCE WS-TOTAL
           DISPLAY "AMOUNT = " WS-AMOUNT
           DISPLAY "VAT    = " WS-VAT
           DISPLAY "TOTAL  = " WS-TOTAL
           GOBACK.

      *>--- โปรแกรมย่อย ---
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALC-VAT.
       DATA DIVISION.
       LINKAGE SECTION.
       01  LS-AMOUNT   PIC 9(7)V99.
       01  LS-RATE     PIC 9(2)V99.
       01  LS-VAT      PIC 9(7)V99.
       01  LS-TOTAL    PIC 9(7)V99.
       PROCEDURE DIVISION USING LS-AMOUNT LS-RATE LS-VAT LS-TOTAL.
           COMPUTE LS-VAT ROUNDED = LS-AMOUNT * LS-RATE / 100
           COMPUTE LS-TOTAL       = LS-AMOUNT + LS-VAT
           GOBACK.
```

ผลลัพธ์คือ `AMOUNT = 0001500.00`, `VAT = 0000105.00`, `TOTAL = 0001605.00` จุดสำคัญคือ `WS-AMOUNT` และ `WS-RATE` ส่งแบบ `BY CONTENT` ดังนั้นหากโปรแกรมย่อยเผลอแก้ค่า จะไม่กระทบตัวแปรในโปรแกรมหลัก ส่วน `WS-VAT` และ `WS-TOTAL` ส่งแบบ `BY REFERENCE` จึงรับผลลัพธ์กลับมาได้ นอกจากนี้ **`LINKAGE SECTION` ไม่จองหน่วยความจำจริง** แต่เป็นเพียงแม่แบบ (template) ที่ทาบทับลงบนหน่วยความจำของผู้เรียก ดังนั้นห้ามใส่ `VALUE clause` ในระดับ 01 ของ `LINKAGE SECTION` และการเข้าถึงตัวแปรเหล่านี้ก่อนถูกเรียกจะทำให้โปรแกรมล่ม

## 9. ข้อผิดพลาดที่พบบ่อยของผู้เริ่มต้น

| ข้อผิดพลาด | อาการที่เกิด | วิธีแก้ |
|---|---|---|
| ใช้คำสงวนเป็นชื่อตัวแปร เช่น `TOTAL`, `DATE`, `COUNT` | คอมไพล์ไม่ผ่านพร้อมข้อความที่อ่านไม่รู้เรื่อง | ใส่คำนำหน้าเสมอ เช่น `WS-TOTAL` |
| จุด (period) เกินหรือขาดกลางบล็อก `IF` | ตรรกะทำงานผิดโดยไม่มีข้อความผิดพลาด | ใช้ `END-IF` / `END-PERFORM` ปิดขอบเขตทุกครั้ง |
| ใช้ตัวแปรแสดงผล `PIC ZZ9.99` ในการคำนวณ | คอมไพล์ไม่ผ่าน หรือได้ผลลัพธ์เพี้ยน | แยกตัวแปรคำนวณ (`PIC 9(5)V99`) กับตัวแปรแสดงผลออกจากกัน |
| ลืมใส่ `ROUNDED` ใน `COMPUTE` | ยอดเงินคลาดเคลื่อนสะสมจากการตัดทิ้ง (truncation) | ใส่ `ROUNDED` ทุกครั้งที่มีการหารหรือคูณอัตราส่วน |
| ปลายทางของ `MOVE` เล็กกว่าต้นทาง | ข้อมูลถูกตัดหาย ตัวเลขตัดจากซ้าย ข้อความตัดจากขวา | ตรวจขนาด `PIC` ให้ตรงกัน หรือใช้ `ON SIZE ERROR` |
| ลืมกำหนดค่าเริ่มต้นให้ตัวแปร | ค่าขยะ (garbage) ทำให้ผลลัพธ์สุ่ม | ใส่ `VALUE ZERO` / `VALUE SPACES` หรือใช้ `INITIALIZE` |
| อ่านค่าตัวแปรควบคุมลูปหลังจบ `PERFORM VARYING` แล้วคิดว่าเท่าค่าสุดท้าย | นับจำนวนระเบียนเกินไปหนึ่ง | ใช้ตัวนับแยกต่างหาก หรือลบหนึ่งออก |
| เขียนโค้ดล้ำเข้าไปในคอลัมน์ 73 ขึ้นไป (fixed format) | ส่วนที่เกินถูกตัดทิ้งเงียบ ๆ | จัดโค้ดให้อยู่ในคอลัมน์ 12–72 หรือเปิดโหมด free format |
| ใช้ `STOP RUN` ในโปรแกรมย่อย | โปรแกรมทั้งระบบจบทันที ไม่กลับไปที่ผู้เรียก | ใช้ `GOBACK` เสมอ |
| ใส่ `VALUE` ใน `LINKAGE SECTION` | คอมไพล์ไม่ผ่าน | ย้ายการกำหนดค่าเริ่มต้นไปที่ฝั่งผู้เรียก |

สรุปหลักคิดที่ควรจำ โคบอลไม่ใช่ภาษาที่ออกแบบมาให้เขียนสั้น แต่ออกแบบมาให้ **ระบุทุกอย่างอย่างชัดเจน** โดยเฉพาะเรื่องขนาดและชนิดของข้อมูล ซึ่งเป็นเหตุผลที่ระบบการเงินอายุ 40 ปียังทำงานถูกต้องอยู่ได้ ผู้เริ่มต้นที่มาจากภาษาสมัยใหม่ควรปรับมุมมองสองข้อ ข้อแรกคือ **ข้อมูลมาก่อนตรรกะ** ให้ออกแบบ `DATA DIVISION` ให้เสร็จก่อนเขียน `PROCEDURE DIVISION` ข้อที่สองคือ **ความชัดเจนสำคัญกว่าความสั้น** การเขียน `END-IF` และ `ROUNDED` ทุกจุดไม่ใช่ความยืดเยื้อ แต่เป็นการป้องกันข้อผิดพลาดที่มีมูลค่าเป็นเงินจริง
