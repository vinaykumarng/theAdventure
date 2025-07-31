import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers


def getResponse(name,story_theme):
    ### LLM model
    llm = CTransformers(model='model/llama-2-7b-chat.ggmlv3.q8_0.bin',
                        model_type='llama',
                        config={'max_new_tokens': 512,
                                'temperature': 0.01})

    # prompt template
    template = (
        "Create an engaging and imaginative {story_theme} story with a clear beginning, middle, and end. "
        "The main character is named {name}, and they should face an interesting challenge or adventure. "
        "Include vivid descriptions, emotions, and a satisfying resolution. "
        "Keep it suitable for all ages and under 500 words."
    )

    prompt = PromptTemplate(input_variables=["name","story_theme"],template=template)

    ## generate the response
    response = llm(prompt.format(name=name,story_theme=story_theme))
    print(response)
    return response


## frontend streamlit
st.set_page_config(page_title='story teller',
                   page_icon='🧚',
                   layout='centered',
                   initial_sidebar_state='collapsed')

st.header("Generate Your Story! Be the main Character!!!")

name = st.text_input("Enter Your Name",placeholder="e.g., John Doe")
story_theme = st.selectbox("Select Theme",["Fun","Horror","Fantasy","Fiction"],index=None,placeholder="Select Theme")

submit = st.button("Generate")

if submit:
    story = getResponse(name,story_theme)
    st.markdown("### 📝 Your Story:")
    st.write(story)