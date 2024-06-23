import streamlit as st
import boto3
import json
import logging
import cmn_settings
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AWS_REGION = cmn_settings.AWS_REGION

bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

opt_model_id_list = [
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
]

with st.sidebar:
    opt_model_id = st.selectbox(label="Model ID", options=opt_model_id_list, index = 0, key="model_id")
    opt_temperature = st.slider(label="Temperature", min_value=0.0, max_value=1.0, value=0.1, step=0.1, key="temperature")
    opt_top_p = st.slider(label="Top P", min_value=0.0, max_value=1.0, value=1.0, step=0.1, key="top_p")
    opt_top_k = st.slider(label="Top K", min_value=0, max_value=500, value=250, step=1, key="top_k")
    opt_max_tokens = st.slider(label="Max Tokens", min_value=0, max_value=4096, value=2048, step=1, key="max_tokens")
    opt_system_msg = st.text_area(label="System Message", value="", key="system_msg")

st.title("💬 Chatbot")


if "menu_chat_messages" not in st.session_state:
    st.session_state["menu_chat_messages"] = [ ]


idx = 1
for msg in st.session_state.menu_chat_messages:
    idx = idx + 1
    content = msg["content"]
    with st.chat_message(msg["role"]):
        st.write(content)
        #if "assistant" == msg["role"]:

if prompt := st.chat_input():
    
    message_history = st.session_state.menu_chat_messages.copy()
    message_history.append({"role": "user", "content": prompt})

    st.chat_message("user").write(prompt)

    request = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": opt_temperature,
        "top_p": opt_top_p,
        "top_k": opt_top_k,
        "max_tokens": opt_max_tokens,
        "system": opt_system_msg,
        "messages": message_history
    }
    
    #json.dumps(request, indent=3)

    try:
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId = opt_model_id,
            contentType = "application/json", #guardrailIdentifier  guardrailVersion=DRAFT, trace=ENABLED | DISABLED
            accept = "application/json",
            body = json.dumps(request))

        result_text = ""
        with st.chat_message("assistant"):
            result_container = st.container(border=True)
            result_area = st.empty()
            stream = response["body"]
            for event in stream:

                if "chunk" in event:

                    chunk = json.loads(event["chunk"]["bytes"])

                    if chunk['type'] == 'message_start':
                        pass

                    elif chunk['type'] == 'message_delta':
                        pass

                    elif chunk['type'] == 'content_block_delta':
                        if chunk['delta']['type'] == 'text_delta':
                            text = chunk['delta']['text']
                            result_text += f"{text}"
                            result_area.write(result_text)

                    elif chunk['type'] == 'message_stop':
                        invocation_metrics = chunk['amazon-bedrock-invocationMetrics']
                        input_token_count = invocation_metrics["inputTokenCount"]
                        output_token_count = invocation_metrics["outputTokenCount"]
                        latency = invocation_metrics["invocationLatency"]
                        lag = invocation_metrics["firstByteLatency"]
                        stats = f"| token.in={input_token_count} token.out={output_token_count} latency={latency} lag={lag}"

                elif "internalServerException" in event:
                    exception = event["internalServerException"]
                    result_text += f"\n\{exception}"
                    result_area.write(result_text)
                elif "modelStreamErrorException" in event:
                    exception = event["modelStreamErrorException"]
                    result_text += f"\n\{exception}"
                    result_area.write(result_text)
                elif "modelTimeoutException" in event:
                    exception = event["modelTimeoutException"]
                    result_text += f"\n\{exception}"
                    result_area.write(result_text)
                elif "throttlingException" in event:
                    exception = event["throttlingException"]
                    result_text += f"\n\{exception}"
                    result_area.write(result_text)
                elif "validationException" in event:
                    exception = event["validationException"]
                    result_text += f"\n\{exception}"
                    result_area.write(result_text)
                else:
                    result_text += f"\n\nUnknown Token"
                    result_area.write(result_text)

        st.session_state.menu_chat_messages.append({"role": "user", "content": prompt})
        st.session_state.menu_chat_messages.append({"role": "assistant", "content": result_text})

    except ClientError as err:
        message = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", message)
        print("A client error occured: " + format(message))
        st.chat_message("system").write(message)