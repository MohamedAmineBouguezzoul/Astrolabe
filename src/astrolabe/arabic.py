"""
Classical Islamic Astrolabe - Arabic Shaping & Bidirectional Text Engine
معالجة الحروف العربية، التشكيل السياقي، وإعادة الترتيب ثنائي الاتجاه وحساب الجمل
"""

import re


class ArabicFormatter:
    """
    Pure-Python contextual shaper, BiDi reordering engine, and numeral converter
    for authentic Islamic and historical astrolabe inscriptions.
    """
    # Mapping of Arabic characters to Unicode Presentation Forms-B
    # (isolated, final, initial, medial)
    FORMS_TABLE = {
        'ا': (0xFE8D, 0xFE8E, 0xFE8D, 0xFE8E),
        'أ': (0xFE83, 0xFE84, 0xFE83, 0xFE84),
        'إ': (0xFE87, 0xFE88, 0xFE87, 0xFE88),
        'آ': (0xFE81, 0xFE82, 0xFE81, 0xFE82),
        'ب': (0xFE8F, 0xFE90, 0xFE91, 0xFE92),
        'ت': (0xFE95, 0xFE96, 0xFE97, 0xFE98),
        'ث': (0xFE99, 0xFE9A, 0xFE9B, 0xFE9C),
        'ج': (0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0),
        'ح': (0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4),
        'خ': (0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8),
        'د': (0xFEA9, 0xFEAA, 0xFEA9, 0xFEAA),
        'ذ': (0xFEAB, 0xFEAC, 0xFEAB, 0xFEAC),
        'ر': (0xFEAD, 0xFEAE, 0xFEAD, 0xFEAE),
        'ز': (0xFEAF, 0xFEB0, 0xFEAF, 0xFEB0),
        'س': (0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4),
        'ش': (0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8),
        'ص': (0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC),
        'ض': (0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0),
        'ط': (0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4),
        'ظ': (0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8),
        'ع': (0xFEC9, 0xFECA, 0xFECB, 0xFECC),
        'غ': (0xFECD, 0xFECE, 0xFECF, 0xFED0),
        'ف': (0xFED1, 0xFED2, 0xFED3, 0xFED4),
        'ق': (0xFED5, 0xFED6, 0xFED7, 0xFED8),
        'ك': (0xFED9, 0xFEDA, 0xFEDB, 0xFEDC),
        'ل': (0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0),
        'م': (0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4),
        'ن': (0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8),
        'ه': (0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC),
        'و': (0xFEED, 0xFEEE, 0xFEED, 0xFEEE),
        'ي': (0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4),
        'ى': (0xFEEF, 0xFEF0, 0xFEEF, 0xFEF0),
        'ة': (0xFE93, 0xFE94, 0xFE93, 0xFE94),
        'ء': (0xFE80, 0xFE80, 0xFE80, 0xFE80),
        'ئ': (0xFE89, 0xFE8A, 0xFE8B, 0xFE8C),
        'ؤ': (0xFE85, 0xFE86, 0xFE85, 0xFE86),
    }

    # Letters that do NOT connect to the subsequent (left) letter
    NON_CONNECTING_LEFT = set('اأإآدذرزوؤةءى')

    @classmethod
    def shape_word(cls, word):
        """Converts raw Arabic characters into contextual joined glyphs."""
        n = len(word)
        i = 0
        ligatured = []
        # First pass: Handle Lam-Alef ligatures
        while i < n:
            if i < n - 1 and word[i] == 'ل':
                nxt = word[i + 1]
                prev_conn = (i > 0 and word[i - 1] in cls.FORMS_TABLE and word[i - 1] not in cls.NON_CONNECTING_LEFT)
                if nxt == 'ا':
                    ligatured.append(('لا', prev_conn))
                    i += 2
                    continue
                elif nxt == 'أ':
                    ligatured.append(('لأ', prev_conn))
                    i += 2
                    continue
                elif nxt == 'إ':
                    ligatured.append(('لإ', prev_conn))
                    i += 2
                    continue
                elif nxt == 'آ':
                    ligatured.append(('لآ', prev_conn))
                    i += 2
                    continue
            ligatured.append((word[i], False))
            i += 1

        # Second pass: Determine initial, medial, final, or isolated form
        shaped = []
        m = len(ligatured)
        for j in range(m):
            item, prev_connects_to_me = ligatured[j]
            if item == 'لا':
                shaped.append(chr(0xFEFC if prev_connects_to_me else 0xFEFB))
                continue
            if item == 'لأ':
                shaped.append(chr(0xFEF8 if prev_connects_to_me else 0xFEF7))
                continue
            if item == 'لإ':
                shaped.append(chr(0xFEFA if prev_connects_to_me else 0xFEF9))
                continue
            if item == 'لآ':
                shaped.append(chr(0xFEF6 if prev_connects_to_me else 0xFEF5))
                continue
            if item not in cls.FORMS_TABLE:
                shaped.append(item)
                continue

            connect_prev = False
            if j > 0:
                prev_item, _ = ligatured[j - 1]
                if prev_item in cls.FORMS_TABLE and prev_item not in cls.NON_CONNECTING_LEFT:
                    connect_prev = True

            connect_next = False
            if j < m - 1 and item not in cls.NON_CONNECTING_LEFT:
                nxt_item, _ = ligatured[j + 1]
                if nxt_item in cls.FORMS_TABLE or nxt_item in ('لا', 'لأ', 'لإ', 'لآ'):
                    connect_next = True

            iso, fin, ini, med = cls.FORMS_TABLE[item]
            if connect_prev and connect_next:
                code = med
            elif connect_prev:
                code = fin
            elif connect_next:
                code = ini
            else:
                code = iso
            shaped.append(chr(code))

        return ''.join(shaped)

    @classmethod
    def reshape_text(cls, text):
        """
        Shapes Arabic text and reverses character/word order for Matplotlib's LTR engine.
        Handles pure Arabic phrases as well as mixed Latin-Arabic titles and annotations.
        """
        if not text:
            return ''
        text_str = str(text)

        has_latin = bool(re.search(r'[A-Za-z]', text_str))
        starts_with_arabic = bool(re.match(r'^\s*[\u0600-\u06FF]', text_str))

        if has_latin and not starts_with_arabic:
            # Latin-dominant with embedded Arabic runs (e.g. 'ASTROLABE MATER (أم الأسطرلاب)')
            arabic_pattern = re.compile(
                r'([\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+'
                r'(?:\s+[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+)*)'
            )
            def replace_run(m):
                words = m.group(1).split()
                shaped_words = [cls.shape_word(w)[::-1] for w in words]
                return ' '.join(shaped_words[::-1])

            return arabic_pattern.sub(replace_run, text_str)
        else:
            # Arabic-dominant or pure Arabic: tokenize preserving whitespace tokens cleanly
            raw_tokens = re.findall(r'\S+|\s+', text_str)
            result_tokens = []
            for token in raw_tokens:
                if re.search(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]', token):
                    sub_tokens = re.findall(r'[\u0600-\u064F\u0670-\u06D3\u06D5]+|[^\u0600-\u064F\u0670-\u06D3\u06D5]+', token)
                    sub_res = []
                    for st in sub_tokens:
                        if re.match(r'[\u0600-\u064F\u0670-\u06D3\u06D5]+', st):
                            sub_res.append(cls.shape_word(st)[::-1])
                        else:
                            sub_res.append(st)
                    result_tokens.append(''.join(sub_res))
                else:
                    result_tokens.append(token)
            return ''.join(result_tokens[::-1])

    @classmethod
    def to_jummal(cls, n):
        """
        Converts an integer (1 <= n <= 999) into classical Hisab al-Jummal (Abjad numerals).
        Units (1-9), Tens (10-90), Hundreds (100-900).
        """
        n = int(round(n))
        if n <= 0:
            return ''
        hundreds = {100: 'ق', 200: 'ر', 300: 'ش', 400: 'ت', 500: 'ث', 600: 'خ', 700: 'ذ', 800: 'ض', 900: 'ظ'}
        tens = {10: 'ي', 20: 'ك', 30: 'ل', 40: 'م', 50: 'ن', 60: 'س', 70: 'ع', 80: 'ف', 90: 'ص'}
        units = {1: 'ا', 2: 'ب', 3: 'ج', 4: 'د', 5: 'ه', 6: 'و', 7: 'ز', 8: 'ح', 9: 'ط'}

        res = ''
        h = (n // 100) * 100
        if h in hundreds:
            res += hundreds[h]
        t = ((n % 100) // 10) * 10
        if t in tens:
            res += tens[t]
        u = n % 10
        if u in units:
            res += units[u]
        return res

    @classmethod
    def to_eastern_arabic(cls, n):
        """Converts digits 0-9 into Eastern Arabic numerals (٠-٩)."""
        mapping = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
        return str(n).translate(mapping)

    @classmethod
    def format_number(cls, n, numeral_system='latin'):
        """
        Formats a numerical value according to the specified system:
        - 'abjad' or 'jummal': Hisab al-Jummal (حساب الجمل)
        - 'eastern_arabic' or 'arabic_numerals': Eastern Arabic digits (٠-٩)
        - 'latin' or 'western': Western Arabic digits (0-9)
        """
        sys = str(numeral_system).lower().strip()
        if sys in ('abjad', 'jummal', 'hisab_al_jummal'):
            if n <= 0:
                return ''
            raw = cls.to_jummal(n)
            return cls.reshape_text(raw)
        elif sys in ('eastern_arabic', 'eastern', 'arabic_numerals', 'hindi', 'mashriqi'):
            return cls.to_eastern_arabic(n)
        else:
            return str(n)

    @classmethod
    def format_label(cls, text, language='latin'):
        """Reshapes Arabic labels for Matplotlib if language is Arabic."""
        if str(language).lower().startswith('ar'):
            return cls.reshape_text(text)
        return text
