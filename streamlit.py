import streamlit as st
import numpy as np
import pandas as pd
from pandas import DataFrame
import spacy
import textstat
import pandas as pd
import nltk 
import base64
import re
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('omw-1.4')
from nltk.tokenize import RegexpTokenizer
import pattern
from pattern.en import sentiment
from PIL import Image

# online page configuration (MUST BE ABOVE EVERYTHING ELSE) 
st.set_page_config(
    page_title="HomeDescription Feedback Generator",
    page_icon="🏘",
)

# function to add png from github repo to background 
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
   
# upload the background png from the git
add_bg_from_local('background.png') 

# create a space at the top of the page for appearance 
header = st.container()

# upload logo 
image = Image.open("logo_dashboard.jpg")
st.image(image)

# set the maximum width of the page 
def _max_width_():
    max_width_str = f"max-width: 20000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


_max_width_()

# feedback description generator
st.markdown("<h1 style='text-align: center; font-size: 25px; font-weight: bold'>Our feedback generator provides insights and improvements on home descriptions based on data from Zillow</h1>", unsafe_allow_html=True)

# additional space 
st.markdown("")

# form inputs 
with st.form(key="my_form"):
    st.write("Input your text below")

    # centers the form on the page 
    ce, c1, ce = st.columns([0.07, 5, 0.07])
   
    with c1:
        doc = st.text_area(
            "Paste your text below", 
            height=510,
            # hide the secondary label 
            label_visibility = "collapsed"
        )
        submit_button = st.form_submit_button(label="Get me the data!")
        
        if not submit_button:
            st.stop()
    
# conversion of the flesh reading ease scores     
reading_ease_translation = ""

if 90 <= textstat.flesch_reading_ease(doc) <= 100:
    reading_ease_translation = "Very Easy"
elif 80 <= textstat.flesch_reading_ease(doc) <= 89:
    reading_ease_translation = "Easy"
elif 70 <= textstat.flesch_reading_ease(doc) <= 79:
    reading_ease_translation = "Fairly Easy"
elif 60 <= textstat.flesch_reading_ease(doc) <= 69:
    reading_ease_translation = "Standard"
elif 50 <= textstat.flesch_reading_ease(doc) <= 59:
    reading_ease_translation = "Faily Difficult"
elif 30 <= textstat.flesch_reading_ease(doc) <= 49:
    reading_ease_translation = "Difficult"
else:
    reading_ease_translation = "Very Confusing"
    
# textstat calulcations --> commented code could be leveraged at a later time 
reading_ease = reading_ease_translation
grade_level = "between " + str(textstat.text_standard(doc)) if textstat.text_standard(doc)[0] != '-' else "not available" # deals with errors in the textstat package 
reading_time = textstat.reading_time(doc, ms_per_char=14.69) # average reading time 
sentence_count = textstat.sentence_count(doc)
word_count = len(re.findall(r'\w+', doc))
sentiment = sentiment(doc)
# unpack touple 
polarity = sentiment[0] 
subjectivity = sentiment[1]
# syllable_count = textstat.syllable_count(doc)
# letter_count = textstat.letter_count(doc)
# polysyllable_count = textstat.polysyllabcount(doc)
# monosyllable_count = textstat.monosyllabcount(doc)    
   
# hard-coded values from our EDA process (after outlier removal) --> Zillow pull Gary shared     
avg_subjectivity = .525
avg_sentence_count = 9
avg_reading_time = 12.01
avg_polarity = .378
avg_word_count = 155

# Deltas for the metric --> commented code could be leveraged at a later time 
delta_reading_time = reading_time - avg_reading_time
delta_sentence_count = sentence_count - avg_sentence_count
delta_word_count = word_count - avg_word_count
delta_polarity = polarity - avg_polarity
delta_subjectivity = subjectivity - avg_subjectivity
#delta_letter_count = letter_count - avg_letter_count
#delta_polysyllable_count = polysyllable_count - avg_polysyllable_count
#delta_monosyllable_count = monosyllable_count - avg_monosyllable_count
#delta_syllable_count = syllable_count - avg_syllable_count

# Summary Section 
st.markdown("# **Summary**")

metric_text = '<body> <span style=color:#FFFFFF;"> Metrics in </span> <span style=color:#FF0000;"> red </span> <span style=color:#FFFFFF;"> or </span> <span style=color:#4CBB17;"> green </span> <span style=color:#FFFFFF;"> preceeded by the arrow show how your description compares to that of homes that sold quickly and for a price higher than the Zestimate. </span> </body>'

st.markdown(metric_text, unsafe_allow_html=True)

# additional spaces 
st.markdown("")
st.markdown("")

# output grade level above the chart 
st.metric("Grade Level", grade_level)

# set double rows of columns for summary table 
c1, c2, c3 = st.columns([1, 1.3, 1])
c11, c22, c33 = st.columns([1, 1.3, 1])

# fill column boxes with metrics --> commented code could be leveraged at a later time 
c1.metric('Sentence Count', sentence_count, delta = delta_sentence_count)
c2.metric("Reading Ease", reading_ease, help = "The readability of a document calculated using the Flesh Reading Ease Score.")
c3.metric('Polarity', round(polarity, 2), delta = round(delta_polarity, 2), help = "How polarizing a given text is. Negative values represent negative sentiment and positive values represent the opposite. The closer the number to 0, the more neutral.")
c11.metric("Word Count", word_count, delta = delta_word_count)
c22.metric("Reading Time (ms)", reading_time, delta = round(delta_reading_time, 2), help = "The time it takes to read a given text.")
c33.metric('Subjectivity', round(subjectivity, 2), delta = round(delta_subjectivity, 2), help = "Values closer to 0 are objective and values closer to 1 are subjective.")
#c1.metric('Syllable Count', syllable_count) #, delta = delta_syllable_count)
#c3.metric('Letter Count', letter_count, delta = delta_letter_count)
#c4.metric('Polysyllable Count', polysyllable_count, delta = delta_polysyllable_count)
#c5.metric('Monosyllable Count', monosyllable_count, delta = delta_monosyllable_count)

# additional spaces 
st.markdown("")
st.markdown("")

# results section 
st.markdown("# **Results**")
st.markdown("An “ideal” description is calculated based on the homes with favorable selling speeds and prices. ")
st.markdown("")

# grade level output 
if (grade_level != "not available"): 
    # if statement removes grade levels that are in the #rd (e.g. 3rd) grade range. Also deals with 9th grade level. 
    if (textstat.text_standard(doc)[1] == 't' and textstat.text_standard(doc)[0] != '9' or textstat.text_standard(doc)[1] == 'r'): 
        st.markdown("### **Grade Level** ❌")
        description = "Your description is written at a " + str(textstat.text_standard(doc)) + " level."
        html_str_level = f"""
        <style> 
        p.a {{ 
        font: bold 20px Arial; 
        color: #82c0cc; 
        }} 
        </style> 
        <p class = "a">{description}</p>
        """
        st.markdown(html_str_level, unsafe_allow_html=True)
        st.markdown("While this is not the most substantial metric that determines a quality description, most home descriptions on Zillow are written above a 10th grade reading level.")
        too_simplistic = '<body> <span style="color:#FF0000;"> Your description appears to be </span> <span style="color:#FF0000; text-decoration: underline;"> too simplistic.</span> <span style="color:#FF0000;"> Add more vivid language and complex sentences to increase engagement. </span> </body>'
        st.markdown(too_simplistic, unsafe_allow_html=True)
    else:    
        st.markdown("### **Grade Level** ✅")
        description = "Your description is written at a " + str(textstat.text_standard(doc)) + " level."
        html_str_level = f"""
        <style> 
        p.a {{ 
        font: bold 20px Arial; 
        color: #82c0cc; 
        }} 
        </style> 
        <p class = "a">{description}</p>
        """
        st.markdown(html_str_level, unsafe_allow_html=True)
        st.markdown("While this is not the most substantial metric that determines a quality description, most home descriptions on Zillow are written above a 10th grade reading level.")

# if the grade level is not available, add spaces to avoid crowding 
if (grade_level != "not available"): 
    st.markdown("")
    st.markdown("") 

# word count output     
if (delta_word_count < 0):
    st.markdown("### **Word Count** ❌")    
    word_count_description = "Your description is " + str(abs(delta_word_count)) + " words below the ideal description."
    html_word_count_description = f"""
        <style> 
        p.a {{ 
        font: bold 20px Arial; 
        color: #82c0cc; 
        }} 
        </style> 
        <p class = "a">{word_count_description}</p>
        """
    st.markdown(html_word_count_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions contain many words.")
    too_simplistic = '<body> <span style="color:#FF0000;"> Consider adding more words to improve the quality of your description. </span> </body>'
    st.markdown(too_simplistic, unsafe_allow_html=True)
else:
    st.markdown("### **Word Count** ✅")    
    word_count_description = "Your description is " + str(delta_word_count) + " words above the ideal description."
    html_word_count_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{word_count_description}</p>
    """
    st.markdown(html_word_count_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions contain many words.")

st.markdown("")
st.markdown("") 

# sentence count output 
if (delta_sentence_count < 0):
    st.markdown("### **Sentence Count** ❌")  
    sentence_count_description = "Your description is " + str(abs(delta_sentence_count)) + " sentences below the ideal description."
    html_sentence_count_description = f"""
        <style> 
        p.a {{ 
        font: bold 20px Arial; 
        color: #82c0cc; 
        }} 
        </style> 
        <p class = "a">{sentence_count_description}</p>
        """
    st.markdown(html_sentence_count_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions contain many sentences.")
    too_simplistic = '<body> <span style="color:#FF0000;"> Consider adding more sentences to improve the quality of your description. </span> </body>'
    st.markdown(too_simplistic, unsafe_allow_html=True)
else:
    st.markdown("### **Sentence Count** ✅") 
    sentence_count_description = "Your description is " + str(delta_sentence_count) + " sentences above the ideal description."
    html_sentence_count_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{sentence_count_description}</p>
    """
    st.markdown(html_sentence_count_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions contain many sentences.")
    
st.markdown("")
st.markdown("")    

# reading ease output 
# if filters out hard-to-read text ranges and errors outputted by textstat function 
if (100 < textstat.flesch_reading_ease(doc) or textstat.flesch_reading_ease(doc) <= 59):
    st.markdown("### **Reading Ease** ❌")   
    reading_ease_description = "Your description is of " + str(reading_ease) + " reading difficulty."
    html_reading_ease_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{reading_ease_description}</p>
    """
    st.markdown(html_reading_ease_description, unsafe_allow_html=True)
    too_convoluted = '<body> <span style="color:#FF0000;"> Consider clarifying details and simplifying diction to improve the readability of your description. </span> </body>'
    st.markdown(too_convoluted, unsafe_allow_html=True)
else:
    st.markdown("### **Reading Ease** ✅") 
    reading_ease_description = "Your description is of " + str(reading_ease) + " reading difficulty."
    html_reading_ease_description = f"""
        <style> 
        p.a {{ 
        font: bold 20px Arial; 
        color: #82c0cc; 
        }} 
        </style> 
        <p class = "a">{reading_ease_description}</p>
        """
    st.markdown(html_reading_ease_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions are not too convoluted.")

st.markdown("")
st.markdown("")

# polarity output 
# calculate percent difference of polarity 
polarity_calculation = int(100 * (delta_polarity / (delta_polarity + polarity/ 2)))

# deals with negative sentiment 
if (polarity < 0):
    st.markdown("### **Polarity** ❌") 
    polarity_description = "Your description has negative sentiment."
    html_polarity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{polarity_description}</p>
    """
    st.markdown(html_polarity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions have high positive sentiment (polarity).")
    too_negative = '<body> <span style="color:#FF0000;"> Consider adding more positive descriptors to improve the impact of your description. </span> </body>'
    st.markdown(too_negative, unsafe_allow_html=True)

# if the description is any more positive than the original, checkbox 
elif(delta_polarity > 0): 
    st.markdown("### **Polarity** ✅") 
    polarity_description = "Your description is " + str(int(100 * (delta_polarity / (delta_polarity + polarity/ 2)))) + "% more positive than the ideal description."
    html_polarity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{polarity_description}</p>
    """
    st.markdown(html_polarity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions have high positive sentiment.")

# if the description is worse than the ideal, but still within 30% of the polarity of the ideal description 
elif (polarity_calculation <= .3):
    st.markdown("### **Polarity** ✅") 
    #polarity_description = "Your description is " + str(int(100 * (delta_polarity / (delta_polarity + polarity/ 2)))) + "% more positive than the ideal description."
    polarity_description = "Your description is within 30% of the polarity of the ideal description." 
    html_polarity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{polarity_description}</p>
    """
    st.markdown(html_polarity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions have high positive sentiment.")
else:
    st.markdown("### **Polarity** ❌") 
    polarity_description = "Your description is " + str(int(100 * (abs(delta_polarity) / (abs(delta_polarity) + polarity / 2)))) + "% less polarizing than the ideal description."
    html_polarity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{polarity_description}</p>
    """
    st.markdown(html_polarity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions have high positive sentiment.")
    too_simplistic = '<body> <span style="color:#FF0000;"> Consider adding more vivid and positive language to improve the impact of your description. </span> </body>'
    st.markdown(too_simplistic, unsafe_allow_html=True)
   
   
st.markdown("")
st.markdown("")      

# subjectivity output 
# calculate percent difference of subjectivity
subjectivity_calculation = int(100 * (abs(delta_subjectivity) / (abs(delta_subjectivity) + subjectivity / 2)))

# if the description is any more subjective than the original, checkbox 
if (delta_subjectivity > 0):
    st.markdown("### **Subjectivity** ✅")    
    subjectivity_description = "Your description is " + str(int(100 * (delta_subjectivity / (subjectivity + delta_subjectivity/ 2)))) + "% more subjective than the ideal description."
    html_subjectivity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{subjectivity_description}</p>
    """
    st.markdown(html_subjectivity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions are highly opinionated.")

# if the description is worse than the ideal, but still within 30% of the subjectivity of the ideal description 
elif (subjectivity_calculation <= 30):
    st.markdown("### **Subjectivity** ✅")    
    #subjectivity_description = "Your description is " + str(int(100 * (delta_subjectivity / (subjectivity + delta_subjectivity/ 2)))) + "% more subjective than the ideal description."
    subjectivity_description = "Your description is within 30% of the subjectivity of the ideal description." 
    html_subjectivity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{subjectivity_description}</p>
    """
    st.markdown(html_subjectivity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions are highly opinionated.")  
else:
    st.markdown("### **Subjectivity** ❌")    
    subjectivity_description = "Your description is " + str(int(100 * (abs(delta_subjectivity) / (abs(delta_subjectivity) + subjectivity / 2)))) + "% more objective than the ideal description."
    html_subjectivity_description = f"""
    <style> 
    p.a {{ 
    font: bold 20px Arial; 
    color: #82c0cc; 
    }} 
    </style> 
    <p class = "a">{subjectivity_description}</p>
    """
    st.markdown(html_subjectivity_description, unsafe_allow_html=True)
    st.markdown("Ideal home descriptions are highly opinionated.")
    too_simplistic = '<body> <span style="color:#FF0000;"> Add more opinionated and subjective statements to improve the impact of your description. </span> </body>'
    st.markdown(too_simplistic, unsafe_allow_html=True)
   

# Future Ideas
# 1) Tailor the cutoffs for polarity and sentiment
    # within 10 percent is currently an arbitrary cutoff 
# 2) Filter by bedrooms, bathrooms, etc.
    # set up sidebar to select # bedrooms, bathrooms, etc.
    # filter df with side bar selections and return as final_df
    # Double check that averaging of text stats is accurate and makes sense for stated conditions
# 3) Map?
    # https://docs.streamlit.io/library/api-reference/charts/st.map
# 4) Hook live data onto the dashboard
    # Very computationally intensive 
# 5) More tailored NLP reviews 
    # aside from the simple "improve word count" etc. 
  
