import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
from pathlib import Path

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 YouTube Video Downloader")
st.markdown("---")

# Input da URL
url = st.text_input(
    "Cole a URL do vídeo do YouTube:",
    placeholder="https://www.youtube.com/watch?v=..."
)

# Botão para ver opções
if st.button("Ver opções de download", type="primary", use_container_width=True):
    if url:
        try:
            with st.spinner("Carregando informações do vídeo..."):
                # Inicializa o objeto YouTube
                yt = YouTube(url, on_progress_callback=on_progress)
                
                # Armazena no session_state para usar depois
                st.session_state.yt = yt
                st.session_state.streams = yt.streams.filter(progressive=True)
                
            st.success("✅ Vídeo carregado com sucesso!")
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar o vídeo: {str(e)}")
            st.session_state.yt = None
    else:
        st.warning("⚠️ Por favor, insira uma URL válida do YouTube.")

# Mostra as opções se o vídeo foi carregado
if "yt" in st.session_state and st.session_state.yt is not None:
    yt = st.session_state.yt
    
    st.markdown("---")
    
    # Preview do vídeo
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(yt.thumbnail_url, use_container_width=True)
    
    with col2:
        st.subheader(yt.title)
        st.caption(f"👤 {yt.author}")
        st.caption(f"⏱️ Duração: {yt.length // 60}:{yt.length % 60:02d}")
        st.caption(f"👁️ Visualizações: {yt.views:,}")
    
    # Embed do vídeo
    with st.expander("🎬 Assistir prévia"):
        video_id = yt.video_id
        st.video(f"https://www.youtube.com/watch?v={video_id}")
    
    st.markdown("---")
    
    # Opções de download
    st.subheader("⚙️ Configurações de Download")
    
    streams = st.session_state.streams
    
    # Cria lista de opções formatadas
    options = []
    for i, stream in enumerate(streams):
        resolution = stream.resolution or "audio"
        fps = stream.fps or 0
        file_size = stream.filesize_mb
        extension = stream.mime_type.split("/")[1]
        
        label = f"{resolution} - {fps}fps - {file_size:.1f}MB - .{extension}"
        options.append(label)
    
    # Select box para escolher a qualidade
    selected_option = st.selectbox(
        "Escolha a qualidade e formato:",
        options,
        index=0
    )
    
    selected_index = options.index(selected_option)
    selected_stream = streams[selected_index]
    
    # Informações do arquivo selecionado
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Resolução", selected_stream.resolution or "Audio")
    with col2:
        st.metric("FPS", selected_stream.fps or "N/A")
    with col3:
        st.metric("Tamanho", f"{selected_stream.filesize_mb:.1f} MB")
    
    st.markdown("---")
    
    # Botão de download
    if st.button("⬇️ Download", type="primary", use_container_width=True):
        try:
            with st.spinner("Baixando vídeo... Por favor, aguarde."):
                # Define o diretório de download
                download_path = str(Path.home() / "Downloads")
                
                # Faz o download
                output_file = selected_stream.download(
                    output_path=download_path,
                    filename_prefix="YT_"
                )
                
                st.success(f"✅ Download concluído!")
                st.info(f"📁 Arquivo salvo em: {output_file}")
                
                # Oferece o arquivo para download direto pelo navegador
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="💾 Salvar arquivo",
                        data=file,
                        file_name=os.path.basename(output_file),
                        mime="video/mp4",
                        use_container_width=True
                    )
                
        except Exception as e:
            st.error(f"❌ Erro ao fazer download: {str(e)}")

# Instruções
with st.sidebar:
    st.header("📖 Como usar")
    st.markdown("""
    1. Cole a URL do vídeo do YouTube
    2. Clique em "Ver opções de download"
    3. Escolha a qualidade desejada
    4. Clique em "Download"
    5. O vídeo será salvo na pasta Downloads
    
    ---
    
    ### ⚠️ Notas importantes:
    - Respeite os direitos autorais
    - Use apenas para conteúdo permitido
    - Alguns vídeos podem ter restrições
    """)

    st.markdown("---")
    st.caption("Desenvolvido com Streamlit + PyTubeFix")
    st.markdown("🔗 Minha página: [ei-raul.github.io](https://ei-raul.github.io/)")
