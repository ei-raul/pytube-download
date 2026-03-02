import os
import tempfile
from pathlib import Path
from urllib.error import HTTPError

import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress

st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎥",
    layout="centered"
)


def is_streamlit_cloud() -> bool:
    return bool(os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("STREAMLIT_CLOUD"))


def get_download_dir() -> Path:
    # Streamlit Cloud has ephemeral filesystem; /tmp is the safest writable area.
    if is_streamlit_cloud():
        base = Path(tempfile.gettempdir()) / "pytube-downloads"
    else:
        base = Path.home() / "Downloads"
    base.mkdir(parents=True, exist_ok=True)
    return base


def safe_filesize_mb(stream) -> str:
    size_bytes = stream.filesize or stream.filesize_approx
    if not size_bytes:
        return "N/A"
    return f"{size_bytes / (1024 * 1024):.1f}MB"


def format_duration(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def load_video(url: str, retries: int = 2):
    last_error = None
    for _ in range(retries + 1):
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            streams = yt.streams.filter(progressive=True).order_by("resolution").desc()
            if not streams:
                streams = yt.streams.filter(
                    adaptive=True, only_video=True, file_extension="mp4"
                ).order_by("resolution").desc()
            return yt, list(streams)
        except Exception as err:
            last_error = err
    raise last_error


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
                yt, streams = load_video(url)
                st.session_state.yt = yt
                st.session_state.streams = streams

            st.success("✅ Vídeo carregado com sucesso!")
            if not streams:
                st.warning("⚠️ Nenhum stream disponível para este vídeo.")
        except Exception as e:
            if isinstance(e, HTTPError) and e.code == 403:
                st.error(
                    "❌ Erro 403: o YouTube bloqueou temporariamente esta origem (comum em ambiente cloud). "
                    "Tente outro vídeo ou novamente mais tarde."
                )
            else:
                st.error(f"❌ Erro ao carregar o vídeo: {str(e)}")
            with st.expander("Detalhes técnicos do erro"):
                st.code(repr(e))
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
        st.caption(f"⏱️ Duração: {format_duration(yt.length)}")
        st.caption(f"👁️ Visualizações: {yt.views:,}")
    
    # Embed do vídeo
    with st.expander("🎬 Assistir prévia"):
        video_id = yt.video_id
        st.video(f"https://www.youtube.com/watch?v={video_id}")
    
    st.markdown("---")
    
    # Opções de download
    st.subheader("⚙️ Configurações de Download")
    
    streams = st.session_state.streams
    if not streams:
        st.warning("⚠️ Nenhum stream disponível para download neste vídeo.")
        st.stop()
    
    # Cria lista de opções formatadas
    options = []
    stream_map = {}
    for stream in streams:
        resolution = stream.resolution or "audio"
        fps = stream.fps or 0
        file_size = safe_filesize_mb(stream)
        extension = stream.mime_type.split("/")[1]

        label = f"{resolution} - {fps}fps - {file_size} - .{extension} (itag {stream.itag})"
        options.append(label)
        stream_map[label] = stream.itag
    
    # Select box para escolher a qualidade
    selected_option = st.selectbox(
        "Escolha a qualidade e formato:",
        options,
        index=0
    )
    
    selected_stream_itag = stream_map[selected_option]
    selected_stream = next(
        (stream for stream in streams if stream.itag == selected_stream_itag), None
    )
    if selected_stream is None:
        st.error("❌ Falha ao selecionar stream. Recarregue as opções de download.")
        st.stop()
    
    # Informações do arquivo selecionado
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Resolução", selected_stream.resolution or "Audio")
    with col2:
        st.metric("FPS", selected_stream.fps or "N/A")
    with col3:
        st.metric("Tamanho", safe_filesize_mb(selected_stream))
    
    st.markdown("---")
    
    # Botão de download
    if st.button("⬇️ Download", type="primary", use_container_width=True):
        try:
            with st.spinner("Baixando vídeo... Por favor, aguarde."):
                download_dir = get_download_dir()
                output_file = None
                last_error = None

                # Recria o objeto para evitar stream expirada e tenta novamente em caso de falha.
                for _ in range(3):
                    try:
                        fresh_yt = YouTube(url, on_progress_callback=on_progress)
                        fresh_stream = fresh_yt.streams.get_by_itag(selected_stream_itag)
                        if fresh_stream is None:
                            raise RuntimeError("Stream não encontrada para este vídeo.")
                        output_file = fresh_stream.download(
                            output_path=str(download_dir),
                            filename_prefix="YT_",
                        )
                        break
                    except Exception as err:
                        last_error = err
                if output_file is None and last_error:
                    raise last_error

                st.success(f"✅ Download concluído!")
                st.info(f"📁 Arquivo salvo em: {output_file}")

                extension = Path(output_file).suffix.lower()
                mime = "video/mp4" if extension == ".mp4" else "application/octet-stream"
                with open(output_file, "rb") as file:
                    file_bytes = file.read()

                st.download_button(
                    label="💾 Salvar arquivo",
                    data=file_bytes,
                    file_name=os.path.basename(output_file),
                    mime=mime,
                    use_container_width=True,
                )

        except Exception as e:
            if isinstance(e, HTTPError) and e.code == 403:
                st.error(
                    "❌ Erro 403: YouTube bloqueou a tentativa de download neste ambiente. "
                    "Isso é comum no Streamlit Cloud por bloqueio de IP compartilhado."
                )
            else:
                st.error(f"❌ Erro ao fazer download: {str(e)}")
            with st.expander("Detalhes técnicos do erro"):
                st.code(repr(e))

# Instruções
with st.sidebar:
    st.header("📖 Como usar")
    save_location = "/tmp/pytube-downloads (temporário)" if is_streamlit_cloud() else "Downloads"
    st.markdown("""
    1. Cole a URL do vídeo do YouTube
    2. Clique em "Ver opções de download"
    3. Escolha a qualidade desejada
    4. Clique em "Download"
    5. O vídeo será salvo na pasta de destino do ambiente
    
    ---
    
    ### ⚠️ Notas importantes:
    - Respeite os direitos autorais
    - Use apenas para conteúdo permitido
    - Alguns vídeos podem ter restrições
    """)
    st.caption(f"📁 Pasta de destino atual: {save_location}")

    st.markdown("---")
    st.caption("Desenvolvido com Streamlit + PyTubeFix")
    st.markdown("🔗 Minha página: [ei-raul.github.io](https://ei-raul.github.io/)")
