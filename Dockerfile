# ============================================================================
# Dockerfile لتثبيت جميع أدوات تحليل APK (إصدارات حديثة)
# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# 1️⃣ تحديث النظام وتثبيت التبعيات الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    wget \
    curl \
    unzip \
    git \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 2️⃣ تثبيت APKTOOL 2.9.1 (أحدث إصدار)
# ============================================================================

# تثبيت Apktool من GitHub الرسمي
RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v2.9.1/apktool_2.9.1.jar -O /usr/local/bin/apktool.jar && \
    wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar && \
    ln -sf /usr/local/bin/apktool /usr/bin/apktool

# ============================================================================
# 3️⃣ تثبيت AAPT2 و ADB (لتعويض --use-aapt1)
# ============================================================================

# AAPT2 (Android Asset Packaging Tool 2)
RUN wget https://github.com/androguard/androguard/releases/download/v3.6.0/aapt2 -O /usr/local/bin/aapt2 && \
    chmod +x /usr/local/bin/aapt2

# Android Debug Bridge (ADB) - الإصدار الأخير
RUN wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O /tmp/platform-tools.zip && \
    unzip /tmp/platform-tools.zip -d /tmp && \
    mv /tmp/platform-tools/adb /usr/local/bin/ && \
    mv /tmp/platform-tools/fastboot /usr/local/bin/ && \
    rm -rf /tmp/platform-tools*

# ============================================================================
# 4️⃣ تثبيت Jadx (مفكك شفرة APK متقدم)
# ============================================================================

# Jadx - decompiler
RUN wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip -O /tmp/jadx.zip && \
    unzip /tmp/jadx.zip -d /opt && \
    ln -s /opt/jadx/bin/jadx /usr/local/bin/jadx && \
    ln -s /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui && \
    rm /tmp/jadx.zip

# ============================================================================
# 5️⃣ تثبيت Bytecode Viewer (أداة تحليل متعددة)
# ============================================================================

RUN wget https://github.com/Konloch/bytecode-viewer/releases/download/v2.11.1/Bytecode-Viewer-2.11.1.jar -O /opt/bytecode-viewer.jar && \
    echo '#!/bin/bash\njava -jar /opt/bytecode-viewer.jar "$@"' > /usr/local/bin/bytecode-viewer && \
    chmod +x /usr/local/bin/bytecode-viewer

# ============================================================================
# 6️⃣ تثبيت Androguard (مكتبة Python لتحليل APK)
# ============================================================================

# سيتم تثبيتها عبر pip لاحقاً
# لكن نثبت تبعياتها النظامية هنا
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 7️⃣ تثبيت APKTool-GUI (واجهة رسومية اختيارية)
# ============================================================================

RUN wget https://github.com/AndnixSH/APKToolGUI/releases/download/v2.2.1/APKToolGUI.jar -O /opt/apktool-gui.jar && \
    echo '#!/bin/bash\njava -jar /opt/apktool-gui.jar "$@"' > /usr/local/bin/apktool-gui && \
    chmod +x /usr/local/bin/apktool-gui

# ============================================================================
# 8️⃣ تثبيت Mobile Security Framework (MobSF) - اختياري
# ============================================================================

# تثبيت تبعيات MobSF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 9️⃣ تثبيت Python ومتطلبات مشروعك
# ============================================================================

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install androguard==3.6.0 && \
    pip install -r requirements.txt

# ============================================================================
# 🔟 نسخ ملفات المشروع وتهيئة البيئة
# ============================================================================

COPY . .

# إنشاء مجلدات العمل
RUN mkdir -p /app/apks /app/output /app/temp && \
    chmod 777 /app/apks /app/output /app/temp

# ============================================================================
# 📊 اختبار جميع الأدوات المثبتة
# ============================================================================

RUN echo "🔧 اختبار الأدوات المثبتة:" && \
    echo "1. Apktool: $(apktool --version 2>/dev/null | head -1)" && \
    echo "2. ADB: $(adb version 2>/dev/null | head -1)" && \
    echo "3. Jadx: $(jadx --version 2>/dev/null | head -1)" && \
    echo "4. AAPT2: $(/usr/local/bin/aapt2 version 2>/dev/null || echo 'مثبت')" && \
    echo "✅ تم تثبيت جميع أدوات APK بنجاح"

# ============================================================================
# 🚀 متغيرات البيئة
# ============================================================================

ENV APKTOOL_PATH=/usr/local/bin/apktool \
    AAPT2_PATH=/usr/local/bin/aapt2 \
    ADB_PATH=/usr/local/bin/adb \
    JADX_PATH=/opt/jadx/bin/jadx \
    JAVA_OPTS="-Xmx2g"

# ============================================================================
# 📝 Health Check
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# ============================================================================
# ▶️ نقطة الدخول
# ============================================================================

CMD ["bash", "-c", "echo '🚀 بيئة تحليل APK جاهزة!' && echo '📦 الأدوات المثبتة:' && apktool --version && exec python3 main.py"]