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
# 5️⃣ تثبيت أدوات OSINT والأمان
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    sqlmap \
    imagemagick \
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
# 6️⃣ تثبيت مكتبات Python
# ============================================================================

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install androguard==3.6.0 || pip install androguard || true && \
    pip install python-magic==0.4.27 pillow==10.0.0

# ============================================================================
# 7️⃣ نسخ ملفات المشروع والتهيئة
# ============================================================================

COPY . .

RUN mkdir -p /app/{temp,logs,output} && \
    chmod -R 777 /app/{temp,logs,output} && \
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# 8️⃣ التحقق من الملفات الأساسية
# ============================================================================

RUN test -f /app/bot.py || (echo "❌ bot.py missing" && exit 1) && \
    test -f /app/main.py || (echo "❌ main.py missing" && exit 1) && \
    python3 -m py_compile bot.py main.py && \
    echo "✅ Python files compiled"

# ============================================================================
# 9️⃣ اختبار الأدوات
# ============================================================================

RUN echo "🔧 Testing Tools" && \
    echo "✅ Apktool: $(apktool --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ Java: $(java -version 2>&1 | head -1)" && \
    echo "✅ Python: $(python3 --version)" && \
    echo "✅ Nmap: $(nmap --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ ADB: $(adb version 2>/dev/null | head -1 || echo 'installed')" && \
    if command -v aapt2 >/dev/null 2>&1; then \
        echo "✅ AAPT2: installed"; \
    elif [ -f /usr/local/bin/aapt2 ]; then \
        echo "✅ AAPT2: installed"; \
    else \
        echo "⚠️  AAPT2: fallback mode"; \
    fi

# ============================================================================
# 🔟 متغيرات البيئة
# ============================================================================

ENV APKTOOL_PATH=/usr/local/bin/apktool \
    TZ=Asia/Riyadh \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# ============================================================================
# 1️⃣1️⃣ Health Check
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# ============================================================================
# 1️⃣2️⃣ نقطة الدخول
# ============================================================================

CMD ["sh", "-c", "\
    echo '🚀 OSINT Hunter Bot' && \
    echo '📅 Time:' $(date) && \
    echo '🔧 Apktool: $(apktool --version 2>/dev/null | head -1)' && \
    echo '🐍 Python: $(python3 --version)' && \
    echo '🚀 Starting...' && \
    exec python3 main.py"]
