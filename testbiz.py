# Required Applications

import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector

#image to text func:

def image_to_text(path):

  input_img= Image.open(path)

  #converting image to array 
  image_arr= np.array(input_img)

  reader= easyocr.Reader(['en'])
  text= reader.readtext(image_arr, detail=0)

  return text, input_img

#extracted text:

def extracted_text(texts):
    extrd_dict={"Name":[], "Designation":[], "Company_Name":[], "Contact":[], "Email":[], "Website":[],
                "Address":[], "Pincode":[]}
    
    extrd_dict["Name"].append(texts[0])
    extrd_dict["Designation"].append(texts[1])

    for i in range(2,len(texts)):

        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and "-" in texts[i]):
            extrd_dict["Contact"].append(texts[i])
        
        elif "@" in texts[i] and ".com" in texts[i]:
            extrd_dict["Email"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small= texts[i].lower()
            extrd_dict["Website"].append(small)

        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extrd_dict["Pincode"].append(texts[i])

        elif re.match(r'^[A-Za-z]', texts[i]):
            extrd_dict["Company_Name"].append(texts[i])

        else:
            remove_colon= re.sub(r'[,;]','',texts[i])
            extrd_dict["Address"].append(remove_colon)

    for key,value in extrd_dict.items():
        if len(value)>0:
            concadenate=" ".join(value)
            extrd_dict[key] = [concadenate]

        else:
            value= "NA"
            extrd_dict[key] = [value]


    return extrd_dict




#Streamlit Application:

st.set_page_config(layout ="wide")
st.title(":red[BizCardX]: Extracting Business Card Data With OCR:sparkles:")

with st.sidebar:
    st.caption(":violet[Application created by karthik]")
    select=option_menu("Main Menu",["Home", "Upload and Modify", "Delete"])
    
if select == "Home":
    st.header("Welcome to :red[BizCardX] project 🪪")
    st.image(Image.open(r"C:/Users/Ezhil/OneDrive/Desktop/python pro/image2.png"))


elif select == "Upload and Modify":
    img= st.file_uploader("Upload Image Here 👇🏻", type= ["png","jpg","jpeg"])

    if img is not None:
        st.image(img, width=500)

        text_image, input_img= image_to_text(img)

        text_dict = extracted_text(text_image)

        if text_dict:
            st.success("Text is Extracted Successfully")

        df=pd.DataFrame(text_dict)

        #converting image to Bytes

        Image_bytes = io.BytesIO()
        input_img.save(Image_bytes, format="PNG")
        image_data = Image_bytes.getvalue()

        #creating dictionary

        data= {"IMAGE_BY":[image_data]}
        df1= pd.DataFrame(data)

        concat_df= pd.concat([df,df1], axis=1)
        st.dataframe(concat_df)

        button_1= st.button("Save", use_container_width=True)

        if button_1:

            mydb=mysql.connector.connect(host="localhost",user="root",password="@Karthik30",database="bizcard")
            cursor= mydb.cursor(buffered= True)

            #table Creation

            create_table_quary='''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(255),
                                                                                designation varchar(255),
                                                                                company_name varchar(255),
                                                                                contact varchar(255),
                                                                                email varchar(255),
                                                                                website text,
                                                                                address text,
                                                                                pincode varchar(255),
                                                                                image_by LONGBLOB)'''
            cursor.execute(create_table_quary)
            mydb.commit()

            #insert query

            insert_query='''INSERT IGNORE INTO bizcard_details(name,designation,company_name,contact,email,website,
                                                        address,pincode,image_by)
                                                        
                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            datas=concat_df.values.tolist()[0]
            cursor.execute(insert_query,datas)
            mydb.commit()

            st.success("Saved Successfully")

    method= st.radio("Select Method",["None","View","Modify"])

    if method == "None":
        st.write("")

    if method == "View":
        mydb=mysql.connector.connect(host="localhost",user="root",password="@Karthik30",database="bizcard")
        cursor= mydb.cursor(buffered= True)
        #select query

        select_query= "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table= cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table, columns=("Name","Designation","Company_Name","Contact","Email","Website",
                                                "Address","Pincode","Image_by"))
        st.dataframe(table_df)


    elif method == "Modify":
        
        mydb=mysql.connector.connect(host="localhost",user="root",password="@Karthik30",database="bizcard")
        cursor= mydb.cursor(buffered= True)
        #select query

        select_query= "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table= cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table, columns=("Name","Designation","Company_Name","Contact","Email","Website",
                                                "Address","Pincode","Image_by"))
        
        col1,col2= st.columns(2)
        with col1:

            select_name= st.selectbox("Select Name", table_df["Name"])

        df3=table_df[table_df["Name"]==select_name]

        df4=df3.copy()

        

        col1,col2=st.columns(2)
        with col1:
            mo_name= st.text_input("Name",df3["Name"].unique()[0])
            mo_desig= st.text_input("Designation",df3["Designation"].unique()[0])
            mo_comname= st.text_input("Company_Name",df3["Company_Name"].unique()[0])
            mo_contact= st.text_input("Contact",df3["Contact"].unique()[0])
            mo_email= st.text_input("Email",df3["Email"].unique()[0])

            df4["Name"]=mo_name
            df4["Designation"]=mo_desig
            df4["Company_Name"]=mo_comname
            df4["Contact"]=mo_contact
            df4["Email"]=mo_email



        with col2:
            mo_website= st.text_input("Website",df3["Website"].unique()[0])
            mo_address= st.text_input("Address",df3["Address"].unique()[0])
            mo_pincode= st.text_input("Pincode",df3["Pincode"].unique()[0])
            
            df4["Website"]=mo_website
            df4["Address"]=mo_address
            df4["Pincode"]=mo_pincode
            
        st.dataframe(df4)

        col1,col2=st.columns(2)
        with col1:
            button_3= st.button("Modify",use_container_width= True)

        if button_3:
            mydb=mysql.connector.connect(host="localhost",user="root",password="@Karthik30",database="bizcard")
            cursor= mydb.cursor(buffered= True)

            cursor.execute(f"DELETE FROM bizcard_details WHERE Name = '{select_name}'")

            #insert query

            insert_query='''INSERT IGNORE INTO bizcard_details(name,designation,company_name,contact,email,website,
                                                        address,pincode,image_by)
                                                        
                                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

            datas=df4.values.tolist()[0]
            cursor.execute(insert_query,datas)
            mydb.commit()

            st.success("Modifyed Successfully")

elif select== "Delete":
    
    mydb=mysql.connector.connect(host="localhost",user="root",password="@Karthik30",database="bizcard")
    cursor= mydb.cursor(buffered= True)

    col1,col2=st.columns(2)
    with col1:
        select_query= "SELECT name FROM bizcard_details"

        cursor.execute(select_query)
        table1= cursor.fetchall()
        mydb.commit()

        names=[]

        for i in table1:
            names.append(i[0])

        name_select= st.selectbox("SELECT NAME", names)

    with col2:
        select_query= f"SELECT designation FROM bizcard_details WHERE name='{name_select}'"

        cursor.execute(select_query)
        table2= cursor.fetchall()
        mydb.commit()

        designations=[]

        for j in table2:
            designations.append(j[0])

        design_select= st.selectbox("SELECT DESIGNATION", designations)

    if name_select and design_select:
        col1,col2,col3=st.columns(3)

        with col1:
            st.write(f"Selected Name : {name_select}")
            st.write("")
            st.write("")
            st.write("")
            st.write(f"Selected designation : {design_select}")
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")

            remove= st.button("Delete", use_container_width=True)

            if remove:

                cursor.execute(f"DELETE FROM bizcard_details WHERE name ='{name_select}' AND designation ='{design_select}'")
                mydb.commit()

                st.warning("Deleted")

