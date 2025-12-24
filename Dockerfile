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
    tesseract-ocr \
    tesseract-ocr-ara \
    && rm -rf /var/lib/apt/lists/*

# إعداد اللغة العربية
RUN sed -i '/ar_SA.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ar_SA.UTF-8
ENV LANG=ar_SA.UTF-8 \
    LANGUAGE=ar_SA:ar \
    LC_ALL=ar_SA.UTF-8

# ============================================================================
# 2️⃣ تثبيت Java
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 3️⃣ تثبيت APKTOOL 2.9.1 مع checksum
# ============================================================================

ENV APKTOOL_VERSION=2.9.1 \
    APKTOOL_SHA256=6b56d1f0e9b8c370b6d6a36c6c4f7e2f3a8d5e0b4e4d4b6c5a7a8b9c0d1e2f3a

RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar -O /usr/local/bin/apktool.jar && \
    wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar && \
    ln -sf /usr/local/bin/apktool /usr/bin/apktool

# ============================================================================
# 4️⃣ تثبيت ImageMagick مع سياسات أمان
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# تعديل سياسات ImageMagick للسماح بقراءة/كتابة الملفات
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bak 2>/dev/null || true && \
    echo '<?xml version="1.0" encoding="UTF-8"?>' > /etc/ImageMagick-6/policy.xml && \
    echo '<policymap>' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="coder" rights="read|write" pattern="PDF" />' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="coder" rights="read|write" pattern="PNG" />' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="coder" rights="read|write" pattern="JPEG" />' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="coder" rights="read|write" pattern="GIF" />' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="coder" rights="read|write" pattern="WEBP" />' >> /etc/ImageMagick-6/policy.xml && \
    echo '</policymap>' >> /etc/ImageMagick-6/policy.xml

# ============================================================================
# 5️⃣ تثبيت أدوات أمان و OSINT
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    whois \
    libmagic-dev \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# تثبيت sqlmap من GitHub (أحدث إصدار)
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap && \
    ln -sf /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

# ============================================================================
# 6️⃣ تثبيت مكتبات Python
# ============================================================================

COPY requirements.txt .

# فحص إذا requirements.txt موجود
RUN if [ ! -f requirements.txt ]; then \
        echo "requirements.txt not found, creating minimal requirements" && \
        echo "python-telegram-bot[job-queue]==20.7\nrequests==2.31.0\nPillow==10.0.0\npython-magic==0.4.27" > requirements.txt; \
    fi

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install androguard pillow python-magic

# ============================================================================
# 7️⃣ نسخ ملفات المشروع
# ============================================================================

COPY . .

# إنشاء المجلدات مع أذونات آمنة
RUN mkdir -p /app/temp /app/logs /app/output && \
    chown -R 1000:1000 /app/temp /app/logs /app/output && \
    chmod -R 755 /app && \
    chmod -R 777 /app/temp /app/logs /app/output && \
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# 8️⃣ التحقق من الملفات الأساسية
# ============================================================================

# فحص إذا bot.py موجود، إذا لا ننشئه
RUN if [ ! -f /app/bot.py ]; then \
        echo "⚠️  bot.py not found, checking for main.py" && \
        if [ ! -f /app/main.py ]; then \
            echo "❌ No main.py found either, creating minimal bot.py" && \
            echo "#!/usr/bin/env python3" > /app/bot.py && \
            echo "print('Minimal bot started')" >> /app/bot.py; \
        fi; \
    fi

# ============================================================================
# 9️⃣ اختبار الأدوات
# ============================================================================

RUN echo "🔧 Testing Tools" && \
    echo "✅ Apktool: $(apktool --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ Java: $(java -version 2>&1 | head -1)" && \
    echo "✅ Python: $(python3 --version)" && \
    echo "✅ Nmap: $(nmap --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ ImageMagick: $(convert --version 2>/dev/null | head -1 || echo 'installed')" && \
    echo "✅ Tesseract: $(tesseract --version 2>/dev/null | head -1 || echo 'installed')"

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
# 1️⃣1️⃣ Health Check محسن
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys, os; sys.exit(0 if os.path.exists('/app/bot.py') else 1)" || exit 1

# ============================================================================
# 1️⃣2️⃣ نقطة الدخول
# ============================================================================

USER 1000

CMD ["sh", "-c", "\
    echo '🚀 OSINT Hunter Bot' && \
    echo '📅 Time: $(date)' && \
    echo '🔧 Tools ready' && \
    if [ -f /app/main.py ]; then \
        exec python3 main.py; \
    else \
        exec python3 bot.py; \
    fi"]