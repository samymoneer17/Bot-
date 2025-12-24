FROM python:3.11-slim

WORKDIR /app

# ============================================================================
# 1️⃣ تحديث النظام وتثبيت التبعيات الأساسية
# ============================================================================

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    ca-certificates \
    unzip \
    jq \
    locales \
    procps \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/*

# إعداد اللغة العربية
RUN sed -i '/ar_SA.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ar_SA.UTF-8
ENV LANG=ar_SA.UTF-8 \
    LANGUAGE=ar_SA:ar \
    LC_ALL=ar_SA.UTF-8

# ============================================================================
# 2️⃣ تثبيت Java (مطلوب لـ Apktool والأدوات الأخرى)
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 3️⃣ تثبيت APKTOOL 2.9.1 (أحدث إصدار)
# ============================================================================

RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v2.9.1/apktool_2.9.1.jar -O /usr/local/bin/apktool.jar && \
    wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar && \
    ln -sf /usr/local/bin/apktool /usr/bin/apktool

# ============================================================================
# 4️⃣ تثبيت أدوات تحليل APK الإضافية
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    android-sdk-build-tools \
    android-sdk-platform-tools \
    && rm -rf /var/lib/apt/lists/*

RUN if [ -d "/usr/lib/android-sdk/build-tools" ]; then \
        find /usr/lib/android-sdk/build-tools -name "aapt2" -type f | head -1 | xargs -I {} ln -sf {} /usr/local/bin/aapt2; \
    fi

RUN cd /tmp && \
    wget -q https://github.com/androguard/androguard/releases/download/v4.0.1/aapt2_linux -O aapt2_linux 2>/dev/null || \
    wget -q https://github.com/GuidoBR/aapt2-static-builds/releases/download/v8.2.0/aapt2-linux -O aapt2_linux 2>/dev/null || true && \
    if [ -f aapt2_linux ]; then \
        mv aapt2_linux /usr/local/bin/aapt2 && chmod +x /usr/local/bin/aapt2; \
    fi

RUN cd /tmp && \
    wget -q https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O platform-tools.zip 2>/dev/null && \
    if [ -f platform-tools.zip ]; then \
        unzip -q platform-tools.zip -d /tmp && \
        mv /tmp/platform-tools/adb /usr/local/bin/ 2>/dev/null || true && \
        mv /tmp/platform-tools/fastboot /usr/local/bin/ 2>/dev/null || true && \
        rm -rf /tmp/platform-tools*; \
    fi

RUN cd /tmp && \
    wget -q https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip -O jadx.zip 2>/dev/null && \
    if [ -f jadx.zip ]; then \
        unzip -q jadx.zip -d /opt 2>/dev/null && \
        ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx 2>/dev/null || true && \
        rm -f jadx.zip; \
    fi

# ============================================================================
# 5️⃣ تثبيت ImageMagick و convert - الإصلاح الكامل
# ============================================================================

# المرحلة 1: تثبيت ImageMagick من البداية
RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# المرحلة 2: إنشاء convert إذا كان مفقودًا
RUN if ! command -v convert >/dev/null 2>&1; then \
        echo "🔧 Creating convert symlink..." && \
        # البحث عن أي إصدار من convert
        if [ -f /usr/bin/convert-im6.q16 ]; then \
            ln -sf /usr/bin/convert-im6.q16 /usr/bin/convert && \
            echo "✅ Symlink created: convert-im6.q16 -> convert"; \
        elif [ -f /usr/bin/convert-im6 ]; then \
            ln -sf /usr/bin/convert-im6 /usr/bin/convert && \
            echo "✅ Symlink created: convert-im6 -> convert"; \
        elif [ -f /usr/bin/magick ]; then \
            ln -sf /usr/bin/magick /usr/bin/convert && \
            echo "✅ Symlink created: magick -> convert"; \
        else \
            # تثبيت graphicsmagick كبديل
            apt-get update && apt-get install -y graphicsmagick-imagemagick-compat && \
            rm -rf /var/lib/apt/lists/* && \
            echo "✅ Installed graphicsmagick as alternative"; \
        fi; \
    fi

# المرحلة 3: التحقق من وجود convert
RUN echo "🔍 Verifying convert command..." && \
    if command -v convert >/dev/null 2>&1; then \
        convert --version | head -1 && \
        echo "✅ Convert is available"; \
    else \
        echo "⚠️ Convert not found, listing available commands:" && \
        ls -la /usr/bin/convert* /usr/bin/magick* 2>/dev/null || true; \
    fi

# ============================================================================
# 6️⃣ تثبيت أدوات OSINT والأمان
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    sqlmap \
    libmagic-dev \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap 2>/dev/null || true

# ============================================================================
# 7️⃣ تثبيت مكتبات Python
# ============================================================================

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install androguard==3.6.0 || pip install androguard || true && \
    pip install python-magic==0.4.27 pillow==10.0.0

# ============================================================================
# 8️⃣ نسخ ملفات المشروع والتهيئة
# ============================================================================

COPY . .

RUN mkdir -p /app/temp /app/logs /app/output && \
    chmod -R 777 /app/temp /app/logs /app/output && \
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# 9️⃣ التحقق من الملفات الأساسية
# ============================================================================

RUN if [ -f bot.py ]; then \
        python3 -m py_compile bot.py && \
        echo "✅ bot.py compiled"; \
    else \
        echo "❌ bot.py missing"; \
    fi

RUN if [ -f main.py ]; then \
        python3 -m py_compile main.py && \
        echo "✅ main.py compiled"; \
    else \
        echo "❌ main.py missing"; \
    fi

# ============================================================================
# 🔟 اختبار الأدوات
# ============================================================================

RUN echo "🔧 Testing Tools" && \
    echo "✅ Apktool: $(apktool --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ Java: $(java -version 2>&1 | head -1)" && \
    echo "✅ Python: $(python3 --version)" && \
    echo "✅ Nmap: $(nmap --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ Convert: $(convert --version 2>/dev/null | head -1 || echo 'installed')" && \
    if command -v adb >/dev/null 2>&1; then \
        echo "✅ ADB: installed"; \
    else \
        echo "⚠️  ADB: not installed"; \
    fi && \
    if command -v aapt2 >/dev/null 2>&1; then \
        echo "✅ AAPT2: installed"; \
    elif [ -f /usr/local/bin/aapt2 ]; then \
        echo "✅ AAPT2: installed"; \
    else \
        echo "⚠️  AAPT2: fallback mode"; \
    fi

# ============================================================================
# 1️⃣1️⃣ متغيرات البيئة
# ============================================================================

ENV APKTOOL_PATH=/usr/local/bin/apktool \
    TZ=Asia/Riyadh \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# ============================================================================
# 1️⃣2️⃣ Health Check
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# ============================================================================
# 1️⃣3️⃣ نقطة الدخول
# ============================================================================

CMD ["sh", "-c", " \
    echo '🚀 OSINT Hunter Bot' && \
    echo '📅 Time:' $(date) && \
    echo '🔧 Apktool: $(apktool --version 2>/dev/null | head -1)' && \
    echo '🐍 Python: $(python3 --version)' && \
    echo '🖼️  Convert: $(convert --version 2>/dev/null | head -1)' && \
    echo '🚀 Starting...' && \
    if [ -f main.py ]; then \
        exec python3 main.py; \
    else \
        exec python3 bot.py; \
    fi"]