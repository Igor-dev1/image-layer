@echo off
REM Inicia o aplicativo Streamlit localmente

pushd "%~dp0"

echo.
echo ==========================================
echo  Abrindo Processador de Imagens (Streamlit)
echo ==========================================
echo.

python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo Houve um erro ao tentar iniciar o Streamlit.
    echo Verifique se o Python e o pacote streamlit estao instalados.
    pause
)

popd
