from data.session_state import logged_user, logged_user_password
from data.user_data import logged_user_name, logged_user_document
from dictionary.vars import field_names, to_remove_list
from dictionary.sql import search_accounts_query, check_user_passwords_quantity_query
from functions.query_executor import QueryExecutor
from functions.login import User
from time import sleep
import streamlit as st


class Passwords:

    def __init__(self) -> None:

        query_executor = QueryExecutor()
        user = User()
        
        def create_new_password():

            col1, col2, col3 = st.columns(3)

            with col2:

                with st.expander(label="Dados", expanded=True):

                    site = st.text_input(label='Nome Site',)
                    url = st.text_input(label='URL/Link do Site')
                    login = st.text_input(label='Login', help="Seu usuário no site")
                    password = st.text_input(label="Senha", type="password", help="Sua senha do site")
                    confirm_values = st.checkbox(label="Confirmar dados", value=False)

                send_button = st.button(':floppy_disk: Cadastrar Senha')

                if send_button and confirm_values == True:

                    with st.spinner(text="Aguarde..."):
                        sleep(2.5)

                    if site != '' and url != '' and login != '' and password != '':

                        insert_password_query = "INSERT INTO senhas(nome_site, url_site, login, senha, usuario_associado, documento_usuario_associado) VALUES(%s, %s, %s, %s, %s, %s)"
                        query_values = (site, url, login, password, logged_user_name, logged_user_document)

                        query_executor.insert_query(query=insert_password_query, values=query_values, success_message='Senha cadastrada com sucesso!', error_message='Erro ao cadastrar senha:')

                        log_query = '''INSERT INTO logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES(%s, %s, %s)'''
                        log_query_values = (logged_user, 'Cadastro', 'Cadastrou a senha {} associada ao email {}'.format(query_values[0], query_values[3]))
                        query_executor.insert_query(query=log_query, values=log_query_values, success_message='Log gravado.', error_message='Erro ao gravar log:')
                    
                    else:
                        with col3:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)
                            cl1, col3 = st.columns(2)
                            with col3:
                                st.error('Há um ou mais campos vazios.')

                elif send_button and confirm_values == False:
                    with col3:
                        with st.spinner(text="Aguarde..."):
                            sleep(2.5)
                        cl1, col3 = st.columns(2)
                        with col3:
                            st.warning(body="Você deve confirmar os dados antes de prosseguir.")

        def read_password():

            user_passwords_quantity = query_executor.simple_consult_query(check_user_passwords_quantity_query, params=(logged_user, logged_user_password))
            user_passwords_quantity = query_executor.treat_simple_result(user_passwords_quantity, to_remove_list)
            user_passwords_quantity = int(user_passwords_quantity)

            if user_passwords_quantity == 0:

                col1, col2, col3 = st.columns(3)

                with col2:
                    st.warning(body="Você ainda não possui senhas cadastradas.")

            elif user_passwords_quantity >= 1:

                col1, col2 = st.columns(2)

                user_accounts = []

                accounts = query_executor.complex_consult_query(query=search_accounts_query, params=(logged_user, logged_user_password))
                accounts = query_executor.treat_numerous_simple_result(accounts, to_remove_list)

                for i in range(0, len(accounts)):
                    user_accounts.append(accounts[i])

                with col1:
                    with st.expander(label="Consulta", expanded=True):
                        selected_option = st.selectbox(label="Selecione a conta", options=user_accounts)
                        safe_password = st.text_input(label="Informe sua senha", type="password")
                        confirm_safe_password = st.text_input(label="Confirme sua senha", type="password")
                        confirm_selection = st.checkbox(label="Confirmar seleção")
                    
                    consult_button = st.button(label=":file_folder: Consultar senha")

                account_details_query = '''
                    SELECT 
                        senhas.nome_site,
                        senhas.url_site,
                        senhas.login,
                        senhas.senha
                    FROM
                        senhas
                    WHERE
                        senhas.nome_site = %s
                            AND senhas.usuario_associado = %s
                            AND senhas.documento_usuario_associado = %s;
                '''

                account_details_values = (selected_option, logged_user_name, logged_user_document)

                result_list = query_executor.complex_consult_query(query=account_details_query, params=account_details_values)
                result_list = query_executor.treat_complex_result(values_to_treat=result_list, values_to_remove=to_remove_list)

                if confirm_selection and consult_button:

                    is_password_valid, hashed_password = user.check_login(logged_user, safe_password)

                    if safe_password != "" and confirm_safe_password != "" and safe_password == confirm_safe_password and is_password_valid == True:

                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(2.5)

                            with st.expander(label="Dados", expanded=True):

                                aux_string = ''

                                for i in range(0, len(result_list)):
                                    st.write(field_names[i])
                                    aux_string = str(result_list[i])
                                    if i == 3:
                                        if aux_string[0] == 'b':
                                            aux_string = aux_string.replace('b', '')
                                    st.code(body="{}".format(aux_string))

                                log_query = '''INSERT into logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES(%s, %s, %s)'''
                                query_values = (logged_user, 'Consulta', 'Consultou a senha do site {}'.format(selected_option))
                                query_executor.insert_query(query=log_query, values=query_values, success_message='Log gravado.', error_message='Erro ao gravar log:')

                    elif safe_password != "" and confirm_safe_password != "" and safe_password == confirm_safe_password and is_password_valid == False:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)
                            st.error(body="A senha informada é inválida.")

                    elif safe_password != confirm_safe_password:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)
                            st.error(body="As senhas informadas não coincidem.")

                elif confirm_selection == False and consult_button:
                    with col3:
                        with st.spinner(text="Aguarde..."):
                            sleep(0.5)
                        with st.expander(label="Aviso", expanded=True):
                            st.warning(body="Confirme a seleção antes de realizar a consulta.")
                        
        def update_password():

            user_passwords_quantity = query_executor.simple_consult_query(check_user_passwords_quantity_query, params=(logged_user, logged_user_password))
            user_passwords_quantity = query_executor.treat_simple_result(user_passwords_quantity, to_remove_list)
            user_passwords_quantity = int(user_passwords_quantity)

            if user_passwords_quantity == 0:

                col1, col2, col3 = st.columns(3)

                with col2:
                    st.warning(body="Você ainda não possui senhas cadastradas.")

            elif user_passwords_quantity >= 1:
                    
                col1, col2 = st.columns(2)

                user_accounts = []

                accounts = query_executor.complex_consult_query(query=search_accounts_query, params=(logged_user, logged_user_password))
                accounts = query_executor.treat_numerous_simple_result(accounts, to_remove_list)

                for i in range(0, len(accounts)):
                    user_accounts.append(accounts[i])

                with col1:
                    with st.expander(label="Consulta", expanded=True):
                        selected_option = st.selectbox(label="Selecione a conta", options=user_accounts)
                        safe_password = st.text_input(label="Informe sua senha", type="password")
                        confirm_safe_password = st.text_input(label="Confirme sua senha", type="password")
                        confirm_selection = st.checkbox(label="Confirmar seleção")

                account_details_query = '''
                    SELECT 
                        senhas.nome_site,
                        senhas.url_site,
                        senhas.login,
                        senhas.senha
                    FROM
                        senhas
                    WHERE
                        senhas.nome_site = %s
                            AND senhas.usuario_associado = %s
                            AND senhas.documento_usuario_associado = %s;
                '''

                account_details_values = (selected_option, logged_user_name, logged_user_document)

                result_list = query_executor.complex_consult_query(query=account_details_query, params=account_details_values)
                result_list = query_executor.treat_complex_result(values_to_treat=result_list, values_to_remove=to_remove_list)

                if confirm_selection:

                    is_password_valid, hashed_password = user.check_login(logged_user, safe_password)

                    if safe_password != "" and confirm_safe_password != "" and safe_password == confirm_safe_password and is_password_valid == True:

                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)

                            with st.expander(label="Novos dados", expanded=True):
                                st.info(body="Site: {}".format(selected_option))
                                url = st.text_input(label='URL/Link do Site')
                                login = st.text_input(label='Login', help="Seu usuário no site")
                                password = st.text_input(label="Senha", type="password", help="Sua senha do site")
                                confirm_values = st.checkbox(label="Confirmar dados", value=False)

                            send_button = st.button(':arrows_counterclockwise: Atualizar Senha')
    
                            if confirm_values and send_button:

                                with col2:
                                    with st.spinner(text="Aguarde..."):
                                        sleep(2.5)

                                update_site_query = '''UPDATE senhas SET url_site = %s, login = %s, senha = %s WHERE nome_site = %s AND usuario_associado = %s AND documento_usuario_associado = %s;'''
                                update_site_values = (url, login, password, selected_option, logged_user_name, logged_user_document)

                                query_executor.insert_query(query=update_site_query, values=update_site_values, success_message="Senha atualizada com sucesso!", error_message="Erro ao atualizar senha:")

                                log_query = '''INSERT into logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES(%s, %s, %s)'''
                                query_values = (logged_user, 'Atualização', 'Atualizou a senha do site {}.'.format(selected_option))
                                query_executor.insert_query(query=log_query, values=query_values, success_message='Log gravado.', error_message='Erro ao gravar log:')

                    if safe_password != "" and confirm_safe_password != "" and safe_password == confirm_safe_password and is_password_valid == False:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)
                            st.error(body="A senha informada é inválida.")

                    elif safe_password != "" and confirm_safe_password != "" and safe_password != confirm_safe_password:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)
                            st.error(body="As senhas informadas não coincidem.")

        def delete_password():
            user_passwords_quantity = query_executor.simple_consult_query(check_user_passwords_quantity_query, params=(logged_user, logged_user_password))
            user_passwords_quantity = query_executor.treat_simple_result(user_passwords_quantity, to_remove_list)
            user_passwords_quantity = int(user_passwords_quantity)

            if user_passwords_quantity == 0:

                col1, col2, col3 = st.columns(3)

                with col2:
                    st.warning(body="Você ainda não possui senhas cadastradas.")

            elif user_passwords_quantity >= 1:

                col1, col2 = st.columns(2)

                user_accounts = []

                accounts = query_executor.complex_consult_query(query=search_accounts_query, params=(logged_user, logged_user_password))
                accounts = query_executor.treat_numerous_simple_result(accounts, to_remove_list)

                for i in range(0, len(accounts)):
                    user_accounts.append(accounts[i])

                with col1:
                    with st.expander(label="Consulta", expanded=True):
                        selected_option = st.selectbox(label="Selecione a conta", options=user_accounts)
                        safe_password = st.text_input(label="Informe sua senha", type="password")
                        confirm_safe_password = st.text_input(label="Confirme sua senha", type="password")
                        confirm_selection = st.checkbox(label="Confirmar seleção")

                account_details_query = '''
                    SELECT 
                        senhas.nome_site,
                        senhas.url_site,
                        senhas.login,
                        senhas.senha
                    FROM
                        senhas
                    WHERE
                        senhas.nome_site = %s
                            AND senhas.usuario_associado = %s
                            AND senhas.documento_usuario_associado = %s;
                '''

                account_details_values = (selected_option, logged_user_name, logged_user_document)

                result_list = query_executor.complex_consult_query(query=account_details_query, params=account_details_values)
                result_list = query_executor.treat_complex_result(values_to_treat=result_list, values_to_remove=to_remove_list)

                if confirm_selection:

                    is_password_valid, hashed_password = user.check_login(logged_user, safe_password)

                    if safe_password != "" and confirm_safe_password != "" and safe_password == confirm_safe_password and is_password_valid == True:

                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)

                            with st.expander(label="Dados", expanded=True):

                                aux_string = ''

                                for i in range(0, len(result_list)):
                                    st.write(field_names[i])
                                    aux_string = str(result_list[i])
                                    if i == 3:
                                        if aux_string[0] == 'b':
                                            aux_string = aux_string.replace('b', '')
                                    st.code(body="{}".format(aux_string))

                                confirm_delete_selection = st.checkbox(label="Confirmar exclusão")

                            delete_password_button = st.button(label=":wastebasket: Deletar senha")

                        if confirm_delete_selection and delete_password_button:
                            with col2:
                                with st.spinner(text="Aguarde..."):
                                    sleep(2.5)

                                delete_password_query = '''DELETE senhas FROM senhas WHERE nome_site = %s AND usuario_associado = %s AND documento_usuario_associado = %s;'''
                                delete_password_values = (selected_option, logged_user_name, logged_user_password)

                                query_executor.insert_query(query=delete_password_query, values=delete_password_values, success_message="Senha excluída com sucesso!", error_message="Erro ao excluir senha:")

                                log_query = '''INSERT into logs_atividades (usuario_log, tipo_log, conteudo_log) VALUES(%s, %s, %s)'''
                                query_values = (logged_user, 'Exclusão', 'Excluiu a senha do site {}'.format(selected_option))
                                query_executor.insert_query(query=log_query, values=query_values, success_message='Log gravado.', error_message='Erro ao gravar log:')

                        elif confirm_delete_selection == False and delete_password_button:
                            with col2:
                                with st.spinner(text="Aguarde..."):
                                    sleep(0.5)
                                st.warning(body="Confirme a exclusão da senha.")

                    elif safe_password != "" and confirm_safe_password != "" and safe_password == confirm_safe_password and is_password_valid == False:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)
                            st.error(body="A senha informada é inválida.")

                    elif safe_password != confirm_safe_password:
                        with col2:
                            with st.spinner(text="Aguarde..."):
                                sleep(0.5)
                            st.error(body="As senhas informadas não coincidem.")

        def show_passwords_interface():

            col1, col2, col3 = st.columns(3)

            with col1:
                st.header(body=":lock: Senhas")

            with col2:
                menu_options = ["Cadastrar senha", "Consultar senha", "Atualizar senha", "Deletar senha"]
                password_option = st.selectbox(label="Menu", options=menu_options)
            
            st.divider()

            if password_option == menu_options[0]:
                create_new_password()
            elif password_option == menu_options[1]:
                read_password()
            elif password_option == menu_options[2]:
                update_password()
            elif password_option == menu_options[3]:
                delete_password()

        self.main_menu = show_passwords_interface