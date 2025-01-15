from dictionary.vars import absolute_app_path, dark_theme, server_config, light_theme
from time import sleep
import streamlit as st


class ChangeTheme:
    def __init__(self):

        def change_theme(theme_option: str):

            config_archive: str = absolute_app_path + "/.streamlit/config.toml"

            if theme_option == "Escuro":
                with open(config_archive, "w") as archive:
                    archive.write(dark_theme)
                    archive.write("\n")
                    archive.write(server_config)

            elif theme_option == "Claro":
                with open(config_archive, "w") as archive:
                    archive.write(light_theme)
                    archive.write("\n")
                    archive.write(server_config)
    
        def main_menu():

            col4, col5, col6 = st.columns(3)

            with col4:

                st.subheader(body=":computer: Opções")

                with st.expander(label="Aparência", expanded=True):
                    selected_theme = st.radio(label="Tema", options=["Escuro", "Claro"])

                theme_confirm_option = st.button(label=":white_check_mark: Confirmar opção")

            if selected_theme != "" and theme_confirm_option:
                with col5:
                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)
                        change_theme(selected_theme)
                    sleep(2.5)
                    st.rerun()

        self.main_menu = main_menu