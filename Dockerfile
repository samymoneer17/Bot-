# ============================================================================
# Dockerfile الشامل النهائي - OSINT Hunter Bot
# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# ============================================================================
# 1️⃣ تحديث النظام وتثبيت التبعيات الأساسية
# ============================================================================

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    locales \
    procps \
    nano \
    vim-tiny \
    unzip \
    jq \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# اختبار wget
RUN which wget && echo "✅ wget مثبت:" && wget --version

# إعداد اللغة العربية
RUN sed -i '/ar_SA.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ar_SA.UTF-8
ENV LANG=ar_SA.UTF-8 \
    LANGUAGE=ar_SA:ar \
    LC_ALL=ar_SA.UTF-8 \
    TZ=Asia/Riyadh

# ============================================================================
# 2️⃣ تثبيت Java (مطلوب لـ Apktool)
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

# إنشاء رابط لـ AAPT2
RUN if [ -d "/usr/lib/android-sdk/build-tools" ]; then \
        find /usr/lib/android-sdk/build-tools -name "aapt2" -type f | head -1 | xargs -I {} ln -sf {} /usr/local/bin/aapt2 2>/dev/null || true; \
    fi

# ADB (Android Debug Bridge)
RUN wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O /tmp/platform-tools.zip && \
    unzip /tmp/platform-tools.zip -d /tmp && \
    mv /tmp/platform-tools/adb /usr/local/bin/ && \
    mv /tmp/platform-tools/fastboot /usr/local/bin/ && \
    rm -rf /tmp/platform-tools*

# ============================================================================
# 5️⃣ تثبيت أدوات OSINT والأمان (بدون تعليقات داخلية)
# ============================================================================

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nmap \
    net-tools \
    iputils-ping \
    dnsutils \
    netcat-openbsd \
    imagemagick \
    libmagic-dev \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# تثبيت SQLMap من GitHub
RUN cd /tmp && \
    wget https://github.com/sqlmapproject/sqlmap/archive/refs/heads/master.zip -O sqlmap.zip && \
    unzip sqlmap.zip && \
    mv sqlmap-master /opt/sqlmap && \
    ln -sf /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap && \
    rm -f sqlmap.zip

# محاولة تثبيت Nikto من GitHub
RUN cd /tmp && \
    wget https://github.com/sullo/nikto/archive/refs/heads/master.zip -O nikto.zip 2>/dev/null || true && \
    if [ -f nikto.zip ]; then \
        unzip nikto.zip && \
        mv nikto-master /opt/nikto && \
        ln -sf /opt/nikto/program/nikto.pl /usr/local/bin/nikto && \
        rm -f nikto.zip; \
    else \
        echo "⚠️  Nikto غير متوفر، سيتم تخطيه" && \
        touch /no_nikto; \
    fi

# ============================================================================
# 6️⃣ إصلاح صلاحيات Nmap
# ============================================================================

RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap 2>/dev/null || \
    (echo "⚠️  تحذير: setcap لـ nmap فشل، سيستخدم sudo" && \
     echo "nmap ALL=(ALL) NOPASSWD: /usr/bin/nmap" > /etc/sudoers.d/nmap && \
     chmod 440 /etc/sudoers.d/nmap)

RUN setcap cap_net_raw,cap_net_admin+eip /usr/bin/ping 2>/dev/null || true

# ============================================================================
# 7️⃣ تثبيت مكتبات Python
# ============================================================================

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    androguard==3.6.0 \
    apkutils==2.1.1 \
    pyaxmlparser==0.3.6 \
    python-magic==0.4.27 \
    pillow==10.0.0

# ============================================================================
# 8️⃣ نسخ باقي ملفات المشروع
# ============================================================================

COPY . .

RUN mkdir -p /app/{temp,logs,output,apks,data} && \
    chmod -R 777 /app/{temp,logs,output} && \
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete

# ============================================================================
# 9️⃣ اختبار جميع الأدوات المثبتة
# ============================================================================

RUN echo "🔧 ======= اختبار الأدوات المثبتة =======" && \
    which wget && echo "✅ wget مثبت" && \
    java -version 2>&1 | head -1 && echo "✅ Java مثبت" && \
    apktool --version 2>/dev/null && echo "✅ Apktool 2.9.1 مثبت" || echo "❌ Apktool غير مثبت" && \
    adb version 2>/dev/null | head -1 && echo "✅ ADB مثبت" || echo "⚠️  ADB غير مثبت" && \
    nmap --version 2>/dev/null | head -1 && echo "✅ Nmap مثبت" && \
    which nc && echo "✅ netcat-openbsd مثبت" || echo "⚠️  netcat غير مثبت" && \
    if [ -f /opt/sqlmap/sqlmap.py ]; then \
        echo "✅ SQLMap مثبت (من GitHub)"; \
    else \
        echo "⚠️  SQLMap غير مثبت"; \
    fi && \
    convert --version 2>/dev/null | head -1 && echo "✅ ImageMagick مثبت" || echo "❌ ImageMagick غير مثبت" && \
    python3 --version && echo "✅ Python 3.11 مثبت" && \
    test -f /app/bot.py && echo "✅ bot.py موجود" || echo "❌ bot.py غير موجود" && \
    test -f /app/main.py && echo "✅ main.py موجود" || echo "❌ main.py غير موجود" && \
    echo "🔧 ======================================="

# ============================================================================
# 🔟 متغيرات البيئة
# ============================================================================

ENV APKTOOL_PATH=/usr/local/bin/apktool \
    NMAP_USE_SUDO=true \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# ============================================================================
# 🚀 نقطة الدخول
# ============================================================================

CMD ["sh", "-c", "\
    echo '🚀 =========================================' && \
    echo '🚀 بدء تشغيل OSINT Hunter Bot' && \
    echo '🚀 =========================================' && \
    echo '📅 الوقت: $(date)' && \
    echo '🌐 المنطقة: Asia/Riyadh' && \
    echo '🔧 الإصدارات:' && \
    echo '   • Apktool: $(apktool --version 2>/dev/null | head -1)' && \
    echo '   • Nmap: $(nmap --version 2>/dev/null | head -1)' && \
    echo '   • Python: $(python3 --version)' && \
    echo '🚀 =========================================' && \
    exec python3 main.py"]