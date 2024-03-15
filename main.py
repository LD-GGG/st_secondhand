import os
import streamlit as st
import time
import streamlit_authenticator as stauth
from uuid import uuid1
from pprint import pprint
import yaml
from yaml.loader import SafeLoader

from utils.databaseUtils import ProductDatabaseOperator

# Load authenticator.
with open('./credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


def page():
    current_user = st.session_state["name"]
    pdo = ProductDatabaseOperator()

    # Define sidebar.

    if st.session_state["authentication_status"] == True:
        st.sidebar.divider()
        st.sidebar.markdown("**反诈骗公告：**  \n> 近期有不法分子通过本平台兜售「原味」衣物，造成多名男性用户上当受骗。**凡是原味，都是诈骗！**")
        st.sidebar.divider()
        st.sidebar.markdown(f"**当前用户：** {current_user}")
    
    # Define tabs.
    tab_disclaimer, tab_display, tab_post, tab_my = st.tabs(["免责声明", "浏览在售", "发布二手", "我的发布"])

    with tab_disclaimer:
        with open("./data/disclaimer.txt", "r", encoding="utf-8") as fr:
            disclaimer_text = fr.read()
            fr.close()
        st.markdown(disclaimer_text)

        if st.session_state["authentication_status"] != True:
            st.divider()
            try:
                email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(location="main", 
                                                                                                                             preauthorization=False,
                                                                                                                             fields={'Form name': '用户注册',
                                                                                                                                     'Email': '电子邮箱',
                                                                                                                                     'Username': '用户名',
                                                                                                                                     'Name': "姓名",
                                                                                                                                     'Password': '密码',
                                                                                                                                     'Repeat password': '重复密码',
                                                                                                                                     'Register': '注册'},)
                if email_of_registered_user:
                    with open('./credentials.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.toast(body=':green[**注册成功！**]', icon="🤗")
            except Exception as e:
                st.error(body=e, icon="😕")

    with tab_display:
        product_list = pdo.get_all()
        if product_list == []:
            st.info(body="暂无二手物品发布", icon="😕")
        else:
            st.success(body=f"目前共有{len(product_list)}件二手物品。", icon="🚚")
        product_list.reverse()
        for product in product_list:

            post_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(product["POST_TIME"]))
            product_description = product['DESCRIPTION'].replace("\n", "  \n- ")
            st.markdown(f"**发布时间：** {post_datetime}")
            st.image(product['IMG'], use_column_width="auto")
            st.markdown(fr"""
#### {product['NAME']}  &ensp;  $\large\color{{red}}￥ {product['PRICE']:.2f}$
- {product_description}
 """)
            def show_seller(seller_name: str, seller_contact: str):
                st.toast(f"#### 卖家：:blue[**{seller_name}**]  \n#### 联系方式：:blue[**{seller_contact}**]",)

            st.button(label="感兴趣",
                      help="点击显示卖家信息",
                      key=f"display_interest_{product['ID']}",
                      on_click=show_seller,
                      args=(product["SELLER"], product["MESSAGE"]),
                      type="primary",
                      disabled=True if st.session_state["authentication_status"] != True else False)
            
           

            st.divider()

    if st.session_state["authentication_status"] == True:
        with tab_post:
            # Input fiels.
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                name = st.text_input(label="物品名称", max_chars=20, key="post_name")
            with col2:
                price = st.number_input(label="售出价格", min_value=0.00, max_value=1000.00, value="min", step=0.01, key="post_price")
            description = st.text_area(label="物品描述", height=4, max_chars=200, key="post_description")
            
            img = st.file_uploader(label="物品图片（可选）", type=['png', 'jpg'], key="post_img")
            message = st.text_input(label="联系方式", max_chars=30, key="post_message", help="供意向购买者联络的手机号、地址等，该信息仅注册用户可见，请注意保护个人隐私。")
            
            # Cache images.
            img_cache_path = None
            if img is not None:
                img_extension = img.name.split(".")[-1]
                img_cache_path = os.path.join("./data/img/", f"{uuid1()}.{img_extension}")
                with open(img_cache_path, "wb") as fr:
                    fr.write(img.getvalue())
                    fr.close()

            if st.button(label="发布", 
                        key="post_submit", 
                        on_click=pdo.add_entry, 
                        args=(name, current_user, price, description, message, img_cache_path),
                        type="primary",
                        disabled=False if name != "" and description != "" and img is not None and message != "" else True):
                st.toast(body=":green[发布成功]", icon="🎈")
    else:
        with tab_post:
            st.error(body="请登录后发布！", icon="😕")

    if st.session_state["authentication_status"] == True:
        with tab_my:
            my_product_list = pdo.get_all(seller=current_user)
            if my_product_list == []:
                st.info(body="暂未发布二手物品", icon="😕")
            my_product_list.reverse()
            for product in my_product_list:

                post_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(product["POST_TIME"]))
                product_description = product['DESCRIPTION'].replace("\n", "  \n- ")
                st.markdown(f"**发布时间：** {post_datetime}")
                st.image(product['IMG'], use_column_width="auto")
                st.markdown(fr"""
#### {product['NAME']}  &ensp;  $\large\color{{red}}￥ {product['PRICE']:.2f}$
- {product_description}
 """)
            
                def disable_product(product_id: int):
                    print(product_id)
                    pdo.change_entry_status(id=product_id, new_status="off")
                    st.toast(body=":green[**下架成功！**]", icon="✅")
                    

                st.button(label="下架物品",
                        help="不再展示已售出或不计划售出的二手物品",
                        key=f"disable_{product['ID']}",
                        on_click=disable_product,
                        args=(product["ID"],),
                        type="secondary")
                st.divider()
    else:
        with tab_my:
            st.error(body="请登录后查看！", icon="😕")
            
           

            
        
st.sidebar.markdown("## 🚚二手市场")
authenticator.login(location="sidebar", 
                    max_concurrent_users=20, 
                    fields={"Form name": "用户登录",
                            "Username": "用户名",
                            "Password": "密码",
                            "Login": "登录"})
if st.session_state["authentication_status"]:
    page()
    authenticator.logout(button_name="登出", location="sidebar")
elif st.session_state["authentication_status"] is False:
    page()
    st.sidebar.error('用户或密码错误！')
elif st.session_state["authentication_status"] is None:
    page()
