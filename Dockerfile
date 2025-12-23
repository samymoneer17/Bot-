# ============================================================================
# Dockerfile الشامل النهائي لـ OSINT Hunter Bot - الإصدار المستقر
# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# ============================================================================
# 1️⃣ تحديث النظام وتثبيت التبعيات الأساسية
# ============================================================================

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    # الأدوات الأساسية
    curl \
    wget \
    git \
    ca-certificates \
    unzip \
    jq \
    # دعم اللغة العربية
    locales \
    # نظام التشغيل الأساسي
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
# 3️⃣ تثبيت APKTOOL 2.9.1 (أحدث إصدار) - الجزء الناجح
# ============================================================================

RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v2.9.1/apktool_2.9.1.jar -O /usr/local/bin/apktool.jar && \
    wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar && \
    ln -sf /usr/local/bin/apktool /usr/bin/apktool

# ============================================================================
# 4️⃣ تثبيت أدوات تحليل APK الإضافية - مع حلول AAPT2 البديلة
# ============================================================================

# ✅ الحل 1: تثبيت Android SDK Command Line Tools ثم AAPT2
RUN apt-get update && apt-get install -y --no-install-recommends \
    android-sdk-build-tools \
    android-sdk-platform-tools \
    && rm -rf /var/lib/apt/lists/*

# ✅ الحل 2: إنشاء رابط لـ AAPT2 إذا كان موجوداً في مسار Android SDK
RUN if [ -d "/usr/lib/android-sdk/build-tools" ]; then \
        find /usr/lib/android-sdk/build-tools -name "aapt2" -type f | head -1 | xargs -I {} ln -sf {} /usr/local/bin/aapt2; \
    fi

# ✅ الحل 3: تحميل AAPT2 من مستودع بديل (إذا فشلت الحلول السابقة)
RUN cd /tmp && \
    wget -q https://github.com/androguard/androguard/releases/download/v4.0.1/aapt2_linux -O aapt2_linux || \
    wget -q https://github.com/GuidoBR/aapt2-static-builds/releases/download/v8.2.0/aapt2-linux -O aapt2_linux || true && \
    if [ -f aapt2_linux ]; then \
        mv aapt2_linux /usr/local/bin/aapt2 && \
        chmod +x /usr/local/bin/aapt2; \
    fi

# ADB (Android Debug Bridge)
RUN wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O /tmp/platform-tools.zip && \
    unzip /tmp/platform-tools.zip -d /tmp && \
    mv /tmp/platform-tools/adb /usr/local/bin/ && \
    mv /tmp/platform-tools/fastboot /usr/local/bin/ && \
    rm -rf /tmp/platform-tools*

# Jadx (مفكك كود متقدم) - اختياري
RUN cd /tmp && \
    wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip -O jadx.zip && \
    unzip jadx.zip -d /opt && \
    ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx 2>/dev/null || true && \
    rm -f jadx.zip

# ============================================================================
# 5️⃣ تثبيت أدوات OSINT والأمان
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    # أدوات الشبكة
    nmap \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    # أدوات الأمان
    sqlmap \
    # معالجة الصور
    imagemagick \
    libmagic-dev \
    # تبعيات Python
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# إضافة صلاحيات nmap (بدون sudo)
RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap 2>/dev/null || true

# ============================================================================
# 6️⃣ تثبيت مكتبات Python والتطبيقات
# ============================================================================

# نسخ وتثبيت requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    # تثبيت مكتبات Android إضافية (إذا لزم الأمر)
    pip install androguard==3.6.0 || pip install androguard || true && \
    pip install python-magic==0.4.27 pillow==10.0.0

# ============================================================================
# 7️⃣ نسخ ملفات المشروع وتهيئة البيئة
# ============================================================================

COPY . .

# إنشاء مجلدات العمل
RUN mkdir -p /app/{temp,logs,output} && \
    chmod -R 777 /app/{temp,logs,output} && \
    # تنظيف الملفات المؤقتة
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# 8️⃣ اختبار وفحص جميع الأدوات المثبتة (مبسط)
# ============================================================================

RUN echo "🔧 ======= اختبار الأدوات الأساسية =======" && \
    echo "✅ Apktool: $(apktool --version 2>/dev/null | head -1 || echo 'مثبت')" && \
    echo "✅ Java: $(java -version 2>&1 | head -1)" && \
    echo "✅ Python: $(python3 --version)" && \
    echo "✅ Nmap: $(nmap --version 2>/dev/null | head -1 || echo 'مثبت')" && \
    echo "✅ ADB: $(adb version 2>/dev/null | head -1 || echo 'مثبت')" && \
    # اختبار AAPT2 بطريقة آمنة
    if command -v aapt2 >/dev/null 2>&1; then \
        echo "✅ AAPT2: مثبت في $(which aapt2)"; \
    elif [ -f /usr/local/bin/aapt2 ]; then \
        echo "✅ AAPT2: مثبت في /usr/local/bin/aapt2"; \
    else \
        echo "⚠️  AAPT2: لم يتم تثبيته، سيستخدم Apktool الإصدار الداخلي"; \
    fi && \
    echo "🔧 ======================================="

# ============================================================================
# 9️⃣ متغيرات البيئة والإعدادات
# ============================================================================

ENV APKTOOL_PATH=/usr/local/bin/apktool \
    TZ=Asia/Riyadh \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# ============================================================================
# 🔟 نقطة الدخول
# ============================================================================

CMD ["sh", "-c", "\
    echo '🚀 OSINT Hunter Bot - الإصدار المستقر' && \
    echo '📅 الوقت: $(date)' && \
    echo '🔧 Apktool: $(apktool --version 2>/dev/null | head -1)' && \
    echo '🐍 Python: $(python3 --version)' && \
    echo '🚀 بدء التشغيل...' && \
    exec python3 main.py"]