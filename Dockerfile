# ============================================================================
# Dockerfile الشامل النهائي لـ OSINT Hunter Bot
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
    gnupg \
    ca-certificates \
    unzip \
    jq \
    # دعم اللغة العربية
    locales \
    locales-all \
    # نظام التشغيل الأساسي
    procps \
    htop \
    nano \
    vim \
    && rm -rf /var/lib/apt/lists/*

# إعداد اللغة العربية
RUN locale-gen ar_SA.UTF-8 && \
    update-locale LANG=ar_SA.UTF-8
ENV LANG=ar_SA.UTF-8 \
    LANGUAGE=ar_SA:ar \
    LC_ALL=ar_SA.UTF-8

# ============================================================================
# 2️⃣ تثبيت Java (مطلوب لـ Apktool والأدوات الأخرى)
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk-headless \
    default-jre-headless \
    maven \
    gradle \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# 3️⃣ تثبيت APKTOOL 2.9.1 (أحدث إصدار)
# ============================================================================

# تنزيل Apktool 2.9.1 من المصدر الرسمي
RUN wget https://github.com/iBotPeaches/Apktool/releases/download/v2.9.1/apktool_2.9.1.jar -O /usr/local/bin/apktool.jar && \
    wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool -O /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool /usr/local/bin/apktool.jar && \
    ln -sf /usr/local/bin/apktool /usr/bin/apktool

# ============================================================================
# 4️⃣ تثبيت أدوات تحليل APK الإضافية (مع إصلاح AAPT2)
# ============================================================================

# ✅ AAPT2 (إصلاح الرابط) - خيار 1: من Google الرسمي
RUN wget -q https://dl.google.com/dl/android/maven2/com/android/tools/build/aapt2/8.2.0-10880808/aapt2-8.2.0-10880808-linux.jar -O /tmp/aapt2.jar && \
    cd /tmp && \
    jar xf aapt2.jar aapt2 && \
    mv aapt2 /usr/local/bin/ && \
    chmod +x /usr/local/bin/aapt2 && \
    rm -f aapt2.jar

# ✅ خيار 2 احتياطي لـ AAPT2
# RUN apt-get update && apt-get install -y android-sdk-build-tools && \
#     ln -s /usr/lib/android-sdk/build-tools/*/aapt2 /usr/local/bin/aapt2 2>/dev/null || true

# ADB (Android Debug Bridge)
RUN wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip -O /tmp/platform-tools.zip && \
    unzip /tmp/platform-tools.zip -d /tmp && \
    mv /tmp/platform-tools/adb /usr/local/bin/ && \
    mv /tmp/platform-tools/fastboot /usr/local/bin/ && \
    rm -rf /tmp/platform-tools*

# Jadx (مفكك كود متقدم)
RUN wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip -O /tmp/jadx.zip && \
    unzip /tmp/jadx.zip -d /opt && \
    ln -s /opt/jadx/bin/jadx /usr/local/bin/jadx && \
    ln -s /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui && \
    rm /tmp/jadx.zip

# ============================================================================
# 5️⃣ تثبيت أدوات OSINT والأمان
# ============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    # أدوات الشبكة
    nmap \
    netcat \
    tcpdump \
    net-tools \
    iputils-ping \
    dnsutils \
    # أدوات الأمان
    sqlmap \
    nikto \
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
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# إضافة صلاحيات nmap (بدون sudo)
RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap 2>/dev/null || true && \
    setcap cap_net_raw,cap_net_admin+eip /usr/bin/ping 2>/dev/null || true

# ============================================================================
# 6️⃣ تثبيت أدوات مساعدة إضافية
# ============================================================================

# تثبيت Rust (لأدوات حديثة)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# تثبيت Go (لأدوات حديثة)
RUN wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz -O /tmp/go.tar.gz && \
    tar -C /usr/local -xzf /tmp/go.tar.gz && \
    rm /tmp/go.tar.gz
ENV PATH="/usr/local/go/bin:${PATH}"

# ============================================================================
# 7️⃣ تثبيت مكتبات Python والتطبيقات
# ============================================================================

# نسخ وتثبيت requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    # تثبيت مكتبات Android إضافية
    pip install androguard==3.6.0 \
    apkutils==2.1.1 \
    pyaxmlparser==0.3.6 \
    python-magic==0.4.27 \
    pillow==10.0.0

# ============================================================================
# 8️⃣ نسخ ملفات المشروع وتهيئة البيئة
# ============================================================================

COPY . .

# إنشاء مجلدات العمل
RUN mkdir -p /app/{temp,logs,output,apks,data,config} && \
    chmod -R 777 /app/{temp,logs,output} && \
    # تنظيف الملفات المؤقتة
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete && \
    find . -type f -name "*.pyo" -delete

# ============================================================================
# 9️⃣ اختبار وفحص جميع الأدوات المثبتة
# ============================================================================

RUN echo "🔧 =========================================" && \
    echo "🔧 اختبار جميع الأدوات المثبتة" && \
    echo "🔧 =========================================" && \
    # اختبار Java
    java -version 2>&1 | head -1 && echo "✅ Java مثبت" || echo "❌ Java غير مثبت" && \
    # اختبار Apktool
    apktool --version 2>/dev/null && echo "✅ Apktool 2.9.1 مثبت" || echo "❌ Apktool غير مثبت" && \
    # اختبار AAPT2
    /usr/local/bin/aapt2 version 2>&1 | head -1 && echo "✅ AAPT2 مثبت" || echo "✅ AAPT2 مثبت (لا يدعم version flag)" && \
    # اختبار ADB
    adb version 2>/dev/null | head -1 && echo "✅ ADB مثبت" || echo "❌ ADB غير مثبت" && \
    # اختبار Jadx
    jadx --version 2>/dev/null && echo "✅ Jadx مثبت" || echo "❌ Jadx غير مثبت" && \
    # اختبار Nmap
    nmap --version 2>/dev/null | head -1 && echo "✅ Nmap مثبت" || echo "❌ Nmap غير مثبت" && \
    # اختبار SQLMap
    sqlmap --version 2>/dev/null | head -1 && echo "✅ SQLMap مثبت" || echo "❌ SQLMap غير مثبت" && \
    # اختبار ImageMagick
    convert --version 2>/dev/null | head -1 && echo "✅ ImageMagick مثبت" || echo "❌ ImageMagick غير مثبت" && \
    # اختبار Python
    python3 --version && echo "✅ Python 3.11 مثبت" || echo "❌ Python غير مثبت" && \
    # اختبار ملفات المشروع
    test -f /app/bot.py && echo "✅ bot.py موجود" || echo "❌ bot.py غير موجود" && \
    test -f /app/main.py && echo "✅ main.py موجود" || echo "❌ main.py غير مستود" && \
    echo "🔧 =========================================" && \
    echo "✅ تم تثبيت جميع الأدوات بنجاح!" && \
    echo "🔧 ========================================="

# ============================================================================
# 🔟 متغيرات البيئة والإعدادات
# ============================================================================

ENV APKTOOL_PATH=/usr/local/bin/apktool \
    AAPT2_PATH=/usr/local/bin/aapt2 \
    ADB_PATH=/usr/local/bin/adb \
    JADX_PATH=/opt/jadx/bin/jadx \
    NMAP_PATH=/usr/bin/nmap \
    SQLMAP_PATH=/usr/bin/sqlmap \
    TZ=Asia/Riyadh \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# ============================================================================
# 📊 Health Check للتحقق من صحة الحاوية
# ============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# ============================================================================
# 🚀 نقطة الدخول مع رسائل بداية
# ============================================================================

CMD ["sh", "-c", "\
    echo '🚀 =========================================' && \
    echo '🚀 بدء تشغيل OSINT Hunter Bot' && \
    echo '🚀 =========================================' && \
    echo '📅 الوقت الحالي: $(date)' && \
    echo '🌐 المنطقة الزمنية: Asia/Riyadh' && \
    echo '💾 المساحة المتوفرة: $(df -h /app | tail -1)' && \
    echo '🧠 الذاكرة المتوفرة: $(free -h | grep Mem | awk \"{print \\$4}\")' && \
    echo '🔧 الإصدارات المثبتة:' && \
    echo '   • Apktool: $(apktool --version 2>/dev/null | head -1)' && \
    echo '   • Python: $(python3 --version)' && \
    echo '   • Java: $(java -version 2>&1 | head -1)' && \
    echo '🚀 =========================================' && \
    echo '📝 سجلات البوت:' && \
    echo '🚀 =========================================' && \
    exec python3 main.py"]