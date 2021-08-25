import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import pickle
import math

#######################################################################################

header = st.beta_container()
dataset = st.beta_container()
Exploratory = st.beta_container()
modelTraining = st.beta_container()

with header:
    st.title('Prediksi Harga Rumah di Pulau Jawa')
    st.subheader('Untuk Masyarakat Kelas Ekonomi Menengah Kebawah')

    image = Image.open('rumah.jpg')
    st.image(image, caption='Rumahku Sesuai Saku')
    st.write('Website ini adalah situs properti terdepan dengan berbasis machine learning, tempat terbaik untuk mencari rumah yang siap dijual maupun disewa khususnya di daerah Pulau Jawa. Jika Anda seorang investor, agen properti, atau konsumen yang mencari properti untuk digunakan sendiri, disewakan, atau dibisniskan, maka Anda berada di situs properti yang tepat.')

with dataset:
	st.header('Nama Data dan Variabel')
	st.text('Dataset ini di ambil per tanggal 17 November 2020')

	pprt = pd.read_excel('Cleaning_under_4jt.xlsx')
	pprt = pprt.rename(columns = {'Tittle' : 'TTL', 'Jenis_Properti' : 'TYP', 'Price_c' : 'PRC', 'Bed_room' : 'BDR','Bath_room' : 'BTR', 'Surface_area' : 'SFA',
	                      'Building_area' : 'BDA', 'Electricity' : 'ELY',  'Garage' : 'GRG', 'Certificate' : 'CFT', 'Provinsi' : 'PRV', 'Kota/Kabupaten': 'CAD', 'Location' : 'LOC',
	                      'Price_per_meters' : 'PPM','inst_per_month_c' : 'IPM', 'Image_URL' : 'IMG'} )
	
#######################################################################################

	def drop_dup (pprt):
    
	    #melihat total duplicated values
	    print(f"sum of duplicated values {pprt['TTL'].duplicated().sum()}")
	    
	    drop = pprt['TTL'].drop_duplicates()
	    print('Shape setelah drop duplicate values : {}'. format(drop.shape))
	    
	drop_dup(pprt)
#######################################################################################
		#mendrop duplicated values berdasarkan TTL
	pprt.drop_duplicates(subset ='TTL',keep = False, inplace = True)

	drop_cols = ['TTL', 'TYP', 'LOC', 'IMG']
	pprt_ad = pprt.drop(drop_cols, axis = 1)
	pprt_ad.head()

	st.write(pprt_ad.head())
#######################################################################################

		#### Outlier treament ####

	colnames_numerics_only = ['PRC','BDR', 'BTR','SFA','BDA','ELY','GRG', 'PPM','IPM']
	    
	Q1 = (pprt_ad[colnames_numerics_only]).quantile(0.25)
	Q3 = (pprt_ad[colnames_numerics_only]).quantile(0.75)

	IQR = Q3 - Q1
	maximum = Q3 + (1.5*IQR)
	print('\n Maximum Values from each Variables are: ')
	print(maximum)
	minimum = Q1 - (1.5*IQR)
	print('\n Minimum Values from each Variables are: ')
	print(minimum)

	more_than = (pprt_ad > maximum)
	lower_than = (pprt_ad < minimum)
	pprt_ad_or = pprt_ad.mask(more_than, maximum, axis=1)
	# pprt_ad_or

#######################################################################################
		#### meremove noise pada kamar tidur ####

	s= pprt_ad_or[pprt_ad_or.BDR > 4]
	# s

	pprt_ad_or = pprt_ad_or.drop(labels=[195,260,261,1323,1370,1406,2575,2665,2985,3124,3296,3587], axis=0)
#######################################################################################
		#### meremove noise pada kamar mandi ####
	v= pprt_ad_or[pprt_ad_or.BTR > 3]
	# v

	pprt_ad_or = pprt_ad_or.drop(labels=[1226,3429], axis=0)
#######################################################################################
		#### meremove noise pada luas lahan ####
	b= pprt_ad_or[pprt_ad_or.SFA < 10] 
	# b

	pprt_ad_or = pprt_ad_or.drop(labels=[1764], axis=0)
#######################################################################################
		#### meremove noise pada luas bangunan ####
	b= pprt_ad_or[pprt_ad_or.BDA < 10]
	# b

	pprt_ad_or = pprt_ad_or.drop(labels=[3180], axis=0)
#######################################################################################

with Exploratory:
	st.header('Gambaran Umum')
	st.write('Beberapa grafik ini merupakan gambaran umum dari data rumah, bentuk bar chart akan mempermudah anda unutk menentukan lokasi mana yang akan dijadikan prioritas pencarian dan kriteria apa yang seharusnya disesuaikan dengan kriteria rumah sesuai keinginan.')

#######################################################################################

	import chart_studio.plotly as py
	import seaborn as sns
	import plotly.express as px
	import plotly.graph_objs as go
	# %matplotlib inline
	import plotly.figure_factory as ff

	from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
	init_notebook_mode(connected = True)

#######################################################################################
		# Penjualan Rumah Tebanyak berdasarkan provinsi
	prv_terbanyak = pd.DataFrame(pprt_ad.groupby('PRV')['CAD'].count() )

	fig = px.bar(prv_terbanyak, x =prv_terbanyak.index, y = 'CAD', color = prv_terbanyak.index, 
	             labels = {'x' : 'Provinsi',
	                      'CAD' : 'Jumlah',
	                      'color' : 'Legend'},
	             title = 'Penjualan Rumah Terbanyak di Setiap Provinsi')

	fig.show()
	fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
	st.plotly_chart(fig, use_container_width = True)

######################################################################################
			#Penjualan Rumah Tebanyak berdasarkan kota kabupaten
	cad_terbanyak = pd.DataFrame(pprt_ad.groupby('CAD')['PRV'].count())

	fig_cad = px.bar(cad_terbanyak, x = cad_terbanyak.index, y = 'PRV', color = cad_terbanyak.index,
	                labels = {
	                    'x' : 'Kabupaten Kota',
	                    'PRV' : 'Jumlah',
	                    'color' : 'Legend'},
	                title = 'Kota dan Kabupaten dengan Penjualan Rumah Terbanyak')
	fig_cad.update_layout(barmode = 'stack', xaxis = {'categoryorder' : 'total descending'})
	st.plotly_chart(fig_cad, use_container_width = True)

#######################################################################################
		#membandingkan harga rumah setiap provinsi
	fig_box = px.box(pprt_ad_or, x = 'PRV', y = 'PRC', color = 'PRV', labels = {
	    'PRV' : 'Provinsi',
	    'PRC' : 'Harga Rumah'
	}, title = 'Box Plot Harga Rumah di Setiap Provinsi di Pulau Jawa')

	st.plotly_chart(fig_box, use_container_width = True)
#######################################################################################

with modelTraining:

	###################################################################################
		### Drop Variabel BTR ###

	pprt_ad_or.drop('BTR', inplace = True, axis = 1)

	###################################################################################
		### Feature encoding to categoric variabel ###

	from sklearn.preprocessing import LabelEncoder

	lbl_encode = LabelEncoder()

	pprt_ad_or['CFT'] = lbl_encode.fit_transform(pprt_ad_or['CFT'])
	pprt_ad_or['PRV'] = lbl_encode.fit_transform(pprt_ad_or['PRV'])
	pprt_ad_or['CAD'] = lbl_encode.fit_transform(pprt_ad_or['CAD'])


	#######################################################################################
	pickle_in = open('reg_rf_rev.pkl','rb')
	reg_rf = pickle.load(pickle_in)

		# @app.route('/')
	def welcome():
	    return "Welcome All"

	# @app.route('/predict',methods=["Get"])
	def predict_note_authentication(BDR, SFA, BDA, ELY, GRG, CFT, PRV, CAD, PPM, IPM):
	    
	    """Let's Authenticate the Banks Note 
	    This is using docstrings for specifications.
	    ---
	    parameters:  
	      - name: variance
	        in: query
	        type: number
	        required: true
	      - name: skewness
	        in: query
	        type: number
	        required: true
	      - name: curtosis
	        in: query
	        type: number
	        required: true
	      - name: entropy
	        in: query
	        type: number
	        required: true
	    responses:
	        200:
	            description: The output values
	        
	    """
	    prediction = reg_rf.predict([[BDR, SFA, BDA, ELY, GRG, CFT, PRV, CAD, PPM, IPM]])
	    print(prediction)
	    return prediction


	def main():
		st.title('Prediksi Harga Rumah')
		html_temp = """
	    <div style="background-color:black;padding:10px">
	    <h2 style="color:white;text-align:center;">Tentukan Harga Rumahmu Sekarang! </h2>
	    </div>
	    """

		st.markdown(html_temp,unsafe_allow_html=True)

		st.subheader('Jumlah Kamar Tidur')
		BDR = st.selectbox('', [1,2,3])

		st.subheader('Luas Lahan (dalam meter persegi)')
		SFA = st.slider("",min_value = 60, max_value = 81, value = 60, step = 1)
		
		st.subheader('Luas Bangunan (dalam meter persegi)')
		BDA = st.slider("",min_value = 36, max_value = 51, value = 36, step = 1)
		
		st.subheader('Kapasitas Listrik')
		ELY = st.select_slider('', options=[1300, 1600, 1900, 2200])

		st.subheader('Jumlah Garasi')
		GRG = st.selectbox('', [0,1])

		st.subheader('Jenis Sertifikat Rumah')
		CHOICES_cft = {0: "SHGB(Hak Guna Bangunan)", 1: "SHM(Sertifikat Hak Milik)", 2: "SBP(Seritifikat Belum pecah)",3: "Strata"}
		def format_func(option):
		    return CHOICES_cft[option]
		CFT = st.selectbox("Select option", options=list(CHOICES_cft.keys()), format_func=format_func)
		st.write(f"You selected option {CFT} called {format_func(CFT)}")

		st.subheader('Provinsi')
		CHOICES = {0: "Banten", 1: "Di Yogykarta", 2: "DKI Jakarta",3: "Jawa Timur", 4: "Jawa Tengah", 5: "Jawa Barat"}
		def format_func(option):
		    return CHOICES[option]
		PRV = st.selectbox("Select option", options=list(CHOICES.keys()), format_func=format_func)
		st.write(f"You selected option {PRV} called {format_func(PRV)}")

		st.subheader('Kabupaten/Kota')
		CHOICES_cad = {0: "Jakarta Barat", 1: "Jakarta Pusat", 2: "Jakarta Selatan",3: "Jakarta Timur", 4: "Jakarta Utara", 5: "Kabupaten Bandung",
		6: "Kabupaten Bandung Barat", 7: "Kabupaten Bantul",8: "Kabupaten Banyumas",9: "Kabupaten Bekasi",10: "Kabupaten Bogor",11: "Kabupaten Bojonegoro",
		12: "Kabupaten Boyolali",13: "Kabupaten Ciamis",14: "Kabupaten Cianjur",15: "Kabupaten Cirebon",16: "Kabupaten Gresik",17: "Kabupaten Gunung Kidul",
		18: "Kabupaten Jember",19: "Kabupaten Karanganyar",20: "Kabupaten Karawang",21: "Kabupaten Kendal",22: "Kabupaten Klaten",23: "Kabupaten Lamongan",
		24: "Kabupaten Lebak",25: "Kabupaten Magelang",26: "Kabupaten Malang",27: "Kabupaten Mojokerto",28: "Kabupaten Purwakarta",
		29: "Kabupaten Serang",30: "Kabupaten Sidoarjo",31: "Kabupaten Sleman",32: "Kabupaten Subang",33: "Kabupaten Sukoharjo",34: "Kabupaten Sumedang",
		35: "Kabupaten Tangerang",36: "Kota Bandung",37: "Kota Batu",38: "Kota Bekasi",39: "Kota Bogor",40: "Kota Cimahi",41: "Kota Cirebon",42: "Kota Depok",
		43: "Kota Malang",44: "Kota Salatiga",45: "Kota Semarang",46: "Kota Surabaya",47: "Kota Surakarta",48: "Kota Tangerang Selatan",
		49: "Kota Yogyakarta"}
		def format_func(option):
		    return CHOICES_cad[option]
		CAD = st.selectbox("Select option", options=list(CHOICES_cad.keys()), format_func=format_func)
		st.write(f"You selected option {CAD} called {format_func(CAD)}")

		st.subheader('Harga Rumah per Meter')
		PPM = st.slider("",min_value = 4000000, max_value = 9000000, value = 4000000, step = 100)

		st.subheader('Cicilan per Bulan')
		IPM = st.slider("",min_value = 1000000, max_value = 4000000, value = 1000000, step = 100)




		result=""
		if st.button("Predict"):
			result=predict_note_authentication(BDR,SFA,BDA,ELY,GRG,CFT,PRV,CAD,PPM,IPM)
		st.success('Harga Rumah Impianmu Adalah {}'.format(result))
		if st.button("About"):
			st.text("17611038@students.uii.ac.id")
			st.text("Built with Streamlit")
	if __name__=='__main__':
		main()