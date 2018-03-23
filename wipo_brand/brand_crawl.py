# -*- coding: utf-8 -*-
import os
import re
from Queue import Queue
from optparse import OptionParser

import execjs
from gevent import monkey

monkey.patch_all()
import gevent

import requests

js = """var LZString = {
    _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    _f: String.fromCharCode,
    compressToBase64: function(c) {
        if (c == null) {
            return ""
        }
        var a = "";
        var k, h, f, j, g, e, d;
        var b = 0;
        c = LZString.compress(c);
        while (b < c.length * 2) {
            if (b % 2 == 0) {
                k = c.charCodeAt(b / 2) >> 8;
                h = c.charCodeAt(b / 2) & 255;
                if (b / 2 + 1 < c.length) {
                    f = c.charCodeAt(b / 2 + 1) >> 8
                } else {
                    f = NaN
                }
            } else {
                k = c.charCodeAt((b - 1) / 2) & 255;
                if ((b + 1) / 2 < c.length) {
                    h = c.charCodeAt((b + 1) / 2) >> 8;
                    f = c.charCodeAt((b + 1) / 2) & 255
                } else {
                    h = f = NaN
                }
            }
            b += 3;
            j = k >> 2;
            g = ((k & 3) << 4) | (h >> 4);
            e = ((h & 15) << 2) | (f >> 6);
            d = f & 63;
            if (isNaN(h)) {
                e = d = 64
            } else {
                if (isNaN(f)) {
                    d = 64
                }
            }
            a = a + LZString._keyStr.charAt(j) + LZString._keyStr.charAt(g) + LZString._keyStr.charAt(e) + LZString._keyStr.charAt(d)
        }
        return a
    },
    decompressFromBase64: function(g) {
        if (g == null) {
            return ""
        }
        var a = "", d = 0, e, o, m, k, n, l, j, h, b = 0, c = LZString._f;
        g = g.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        while (b < g.length) {
            n = LZString._keyStr.indexOf(g.charAt(b++));
            l = LZString._keyStr.indexOf(g.charAt(b++));
            j = LZString._keyStr.indexOf(g.charAt(b++));
            h = LZString._keyStr.indexOf(g.charAt(b++));
            o = (n << 2) | (l >> 4);
            m = ((l & 15) << 4) | (j >> 2);
            k = ((j & 3) << 6) | h;
            if (d % 2 == 0) {
                e = o << 8;
                if (j != 64) {
                    a += c(e | m)
                }
                if (h != 64) {
                    e = k << 8
                }
            } else {
                a = a + c(e | o);
                if (j != 64) {
                    e = m << 8
                }
                if (h != 64) {
                    a += c(e | k)
                }
            }
            d += 3
        }
        return LZString.decompress(a)
    },
    compressToUTF16: function(d) {
        if (d == null) {
            return ""
        }
        var b = "", e, j, h, a = 0, g = LZString._f;
        d = LZString.compress(d);
        for (e = 0; e < d.length; e++) {
            j = d.charCodeAt(e);
            switch (a++) {
            case 0:
                b += g((j >> 1) + 32);
                h = (j & 1) << 14;
                break;
            case 1:
                b += g((h + (j >> 2)) + 32);
                h = (j & 3) << 13;
                break;
            case 2:
                b += g((h + (j >> 3)) + 32);
                h = (j & 7) << 12;
                break;
            case 3:
                b += g((h + (j >> 4)) + 32);
                h = (j & 15) << 11;
                break;
            case 4:
                b += g((h + (j >> 5)) + 32);
                h = (j & 31) << 10;
                break;
            case 5:
                b += g((h + (j >> 6)) + 32);
                h = (j & 63) << 9;
                break;
            case 6:
                b += g((h + (j >> 7)) + 32);
                h = (j & 127) << 8;
                break;
            case 7:
                b += g((h + (j >> 8)) + 32);
                h = (j & 255) << 7;
                break;
            case 8:
                b += g((h + (j >> 9)) + 32);
                h = (j & 511) << 6;
                break;
            case 9:
                b += g((h + (j >> 10)) + 32);
                h = (j & 1023) << 5;
                break;
            case 10:
                b += g((h + (j >> 11)) + 32);
                h = (j & 2047) << 4;
                break;
            case 11:
                b += g((h + (j >> 12)) + 32);
                h = (j & 4095) << 3;
                break;
            case 12:
                b += g((h + (j >> 13)) + 32);
                h = (j & 8191) << 2;
                break;
            case 13:
                b += g((h + (j >> 14)) + 32);
                h = (j & 16383) << 1;
                break;
            case 14:
                b += g((h + (j >> 15)) + 32, (j & 32767) + 32);
                a = 0;
                break
            }
        }
        return b + g(h + 32)
    },
    decompressFromUTF16: function(d) {
        if (d == null) {
            return ""
        }
        var b = "", h, j, a = 0, e = 0, g = LZString._f;
        while (e < d.length) {
            j = d.charCodeAt(e) - 32;
            switch (a++) {
            case 0:
                h = j << 1;
                break;
            case 1:
                b += g(h | (j >> 14));
                h = (j & 16383) << 2;
                break;
            case 2:
                b += g(h | (j >> 13));
                h = (j & 8191) << 3;
                break;
            case 3:
                b += g(h | (j >> 12));
                h = (j & 4095) << 4;
                break;
            case 4:
                b += g(h | (j >> 11));
                h = (j & 2047) << 5;
                break;
            case 5:
                b += g(h | (j >> 10));
                h = (j & 1023) << 6;
                break;
            case 6:
                b += g(h | (j >> 9));
                h = (j & 511) << 7;
                break;
            case 7:
                b += g(h | (j >> 8));
                h = (j & 255) << 8;
                break;
            case 8:
                b += g(h | (j >> 7));
                h = (j & 127) << 9;
                break;
            case 9:
                b += g(h | (j >> 6));
                h = (j & 63) << 10;
                break;
            case 10:
                b += g(h | (j >> 5));
                h = (j & 31) << 11;
                break;
            case 11:
                b += g(h | (j >> 4));
                h = (j & 15) << 12;
                break;
            case 12:
                b += g(h | (j >> 3));
                h = (j & 7) << 13;
                break;
            case 13:
                b += g(h | (j >> 2));
                h = (j & 3) << 14;
                break;
            case 14:
                b += g(h | (j >> 1));
                h = (j & 1) << 15;
                break;
            case 15:
                b += g(h | j);
                a = 0;
                break
            }
            e++
        }
        return LZString.decompress(b)
    },
    compress: function(e) {
        if (e == null) {
            return ""
        }
        var h, l, n = {}, m = {}, o = "", c = "", r = "", d = 2, g = 3, b = 2, q = "", a = 0, j = 0, p, k = LZString._f;
        for (p = 0; p < e.length; p += 1) {
            o = e.charAt(p);
            if (!Object.prototype.hasOwnProperty.call(n, o)) {
                n[o] = g++;
                m[o] = true
            }
            c = r + o;
            if (Object.prototype.hasOwnProperty.call(n, c)) {
                r = c
            } else {
                if (Object.prototype.hasOwnProperty.call(m, r)) {
                    if (r.charCodeAt(0) < 256) {
                        for (h = 0; h < b; h++) {
                            a = (a << 1);
                            if (j == 15) {
                                j = 0;
                                q += k(a);
                                a = 0
                            } else {
                                j++
                            }
                        }
                        l = r.charCodeAt(0);
                        for (h = 0; h < 8; h++) {
                            a = (a << 1) | (l & 1);
                            if (j == 15) {
                                j = 0;
                                q += k(a);
                                a = 0
                            } else {
                                j++
                            }
                            l = l >> 1
                        }
                    } else {
                        l = 1;
                        for (h = 0; h < b; h++) {
                            a = (a << 1) | l;
                            if (j == 15) {
                                j = 0;
                                q += k(a);
                                a = 0
                            } else {
                                j++
                            }
                            l = 0
                        }
                        l = r.charCodeAt(0);
                        for (h = 0; h < 16; h++) {
                            a = (a << 1) | (l & 1);
                            if (j == 15) {
                                j = 0;
                                q += k(a);
                                a = 0
                            } else {
                                j++
                            }
                            l = l >> 1
                        }
                    }
                    d--;
                    if (d == 0) {
                        d = Math.pow(2, b);
                        b++
                    }
                    delete m[r]
                } else {
                    l = n[r];
                    for (h = 0; h < b; h++) {
                        a = (a << 1) | (l & 1);
                        if (j == 15) {
                            j = 0;
                            q += k(a);
                            a = 0
                        } else {
                            j++
                        }
                        l = l >> 1
                    }
                }
                d--;
                if (d == 0) {
                    d = Math.pow(2, b);
                    b++
                }
                n[c] = g++;
                r = String(o)
            }
        }
        if (r !== "") {
            if (Object.prototype.hasOwnProperty.call(m, r)) {
                if (r.charCodeAt(0) < 256) {
                    for (h = 0; h < b; h++) {
                        a = (a << 1);
                        if (j == 15) {
                            j = 0;
                            q += k(a);
                            a = 0
                        } else {
                            j++
                        }
                    }
                    l = r.charCodeAt(0);
                    for (h = 0; h < 8; h++) {
                        a = (a << 1) | (l & 1);
                        if (j == 15) {
                            j = 0;
                            q += k(a);
                            a = 0
                        } else {
                            j++
                        }
                        l = l >> 1
                    }
                } else {
                    l = 1;
                    for (h = 0; h < b; h++) {
                        a = (a << 1) | l;
                        if (j == 15) {
                            j = 0;
                            q += k(a);
                            a = 0
                        } else {
                            j++
                        }
                        l = 0
                    }
                    l = r.charCodeAt(0);
                    for (h = 0; h < 16; h++) {
                        a = (a << 1) | (l & 1);
                        if (j == 15) {
                            j = 0;
                            q += k(a);
                            a = 0
                        } else {
                            j++
                        }
                        l = l >> 1
                    }
                }
                d--;
                if (d == 0) {
                    d = Math.pow(2, b);
                    b++
                }
                delete m[r]
            } else {
                l = n[r];
                for (h = 0; h < b; h++) {
                    a = (a << 1) | (l & 1);
                    if (j == 15) {
                        j = 0;
                        q += k(a);
                        a = 0
                    } else {
                        j++
                    }
                    l = l >> 1
                }
            }
            d--;
            if (d == 0) {
                d = Math.pow(2, b);
                b++
            }
        }
        l = 2;
        for (h = 0; h < b; h++) {
            a = (a << 1) | (l & 1);
            if (j == 15) {
                j = 0;
                q += k(a);
                a = 0
            } else {
                j++
            }
            l = l >> 1
        }
        while (true) {
            a = (a << 1);
            if (j == 15) {
                q += k(a);
                break
            } else {
                j++
            }
        }
        return q
    },
    decompress: function(k) {
        if (k == null) {
            return ""
        }
        if (k == "") {
            return null
        }
        var o = [], j, d = 4, l = 4, h = 3, q = "", t = "", g, p, r, s, a, b, n, m = LZString._f, e = {
            string: k,
            val: k.charCodeAt(0),
            position: 32768,
            index: 1
        };
        for (g = 0; g < 3; g += 1) {
            o[g] = g
        }
        r = 0;
        a = Math.pow(2, 2);
        b = 1;
        while (b != a) {
            s = e.val & e.position;
            e.position >>= 1;
            if (e.position == 0) {
                e.position = 32768;
                e.val = e.string.charCodeAt(e.index++)
            }
            r |= (s > 0 ? 1 : 0) * b;
            b <<= 1
        }
        switch (j = r) {
        case 0:
            r = 0;
            a = Math.pow(2, 8);
            b = 1;
            while (b != a) {
                s = e.val & e.position;
                e.position >>= 1;
                if (e.position == 0) {
                    e.position = 32768;
                    e.val = e.string.charCodeAt(e.index++)
                }
                r |= (s > 0 ? 1 : 0) * b;
                b <<= 1
            }
            n = m(r);
            break;
        case 1:
            r = 0;
            a = Math.pow(2, 16);
            b = 1;
            while (b != a) {
                s = e.val & e.position;
                e.position >>= 1;
                if (e.position == 0) {
                    e.position = 32768;
                    e.val = e.string.charCodeAt(e.index++)
                }
                r |= (s > 0 ? 1 : 0) * b;
                b <<= 1
            }
            n = m(r);
            break;
        case 2:
            return ""
        }
        o[3] = n;
        p = t = n;
        while (true) {
            if (e.index > e.string.length) {
                return ""
            }
            r = 0;
            a = Math.pow(2, h);
            b = 1;
            while (b != a) {
                s = e.val & e.position;
                e.position >>= 1;
                if (e.position == 0) {
                    e.position = 32768;
                    e.val = e.string.charCodeAt(e.index++)
                }
                r |= (s > 0 ? 1 : 0) * b;
                b <<= 1
            }
            switch (n = r) {
            case 0:
                r = 0;
                a = Math.pow(2, 8);
                b = 1;
                while (b != a) {
                    s = e.val & e.position;
                    e.position >>= 1;
                    if (e.position == 0) {
                        e.position = 32768;
                        e.val = e.string.charCodeAt(e.index++)
                    }
                    r |= (s > 0 ? 1 : 0) * b;
                    b <<= 1
                }
                o[l++] = m(r);
                n = l - 1;
                d--;
                break;
            case 1:
                r = 0;
                a = Math.pow(2, 16);
                b = 1;
                while (b != a) {
                    s = e.val & e.position;
                    e.position >>= 1;
                    if (e.position == 0) {
                        e.position = 32768;
                        e.val = e.string.charCodeAt(e.index++)
                    }
                    r |= (s > 0 ? 1 : 0) * b;
                    b <<= 1
                }
                o[l++] = m(r);
                n = l - 1;
                d--;
                break;
            case 2:
                return t
            }
            if (d == 0) {
                d = Math.pow(2, h);
                h++
            }
            if (o[n]) {
                q = o[n]
            } else {
                if (n === l) {
                    q = p + p.charAt(0)
                } else {
                    return null
                }
            }
            t += q;
            o[l++] = p + q.charAt(0);
            d--;
            p = q;
            if (d == 0) {
                d = Math.pow(2, h);
                h++
            }
        }
    }
};"""

ctx = execjs.compile(js)
jobs = Queue()

qk_cookie_cache = Queue()

qk_pat = re.compile(".*?qk = \"(.*?)\";", re.S)
dir_path = "/data/brand"


def qk_gen():
    url = "http://www.wipo.int/branddb/en/#"
    r = requests.get(url)
    qk = qk_pat.match(r.text).group(1)
    cookie = r.cookies
    qk_cookie_cache.put((qk, cookie))


def lz_decode(s):
    """
    调用js加密请求参数
    :param s: 
    :return: 
    """
    return ctx.call("LZString.compressToBase64", s)


def form_data(start_num, qk):
    """
    根据起始页面fake请求参数，qi可以一直不变
    :param start_num: 
    :return: 
    """
    return '{"p":{"rows":100,"start":' + str(
        start_num) + '},"type":"brand","la":"en","qi":"0-' + qk + '","queue":1}'


def make_req(page_num, qk, cookie):
    url = "http://www.wipo.int/branddb/jsp/select.jsp"
    headers = {
        'Origin': 'http://www.wipo.int',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'http://www.wipo.int/branddb/en/',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    return requests.post(url, headers=headers, cookies=cookie, data={"qz": lz_decode(form_data(page_num * 30, qk))})


def qk_gen_worker():
    counter = 0
    while not jobs.empty():
        if qk_cookie_cache.qsize() < 30:
            try:
                qk_gen()
            except:
                print "qk gen error"
        counter += 1
        gevent.sleep(0.1)
        if counter % 100 == 0:
            print "now qk size : {s}".format(s=qk_cookie_cache.qsize())


def worker(name):
    def process_error(page_num):
        print "crawl page {num} error".format(num=page_num)
        jobs.put(page_num)

    while not jobs.empty():
        page_num = jobs.get()
        file_path = dir_path + "/{num}.json".format(num=page_num)
        if os.path.exists(file_path):
            print "page {num} already exist".format(num=page_num)
            continue
        print "{name} start crawl page {num}".format(name=name, num=page_num)
        qk, cookie = qk_cookie_cache.get()
        r = make_req(page_num, qk=qk, cookie=cookie)
        if r.status_code == 200:
            item = r.json()
            if "error" in item or len(r.content) < 200:
                process_error(page_num)
            with open(file_path, "w") as f:
                f.write(r.content)
            qk_cookie_cache.put((qk, cookie))
        else:
            process_error(page_num)


def main(start_num, end_num, worker_num):
    for i in range(start_num, end_num):
        jobs.put(i)
    workers = [gevent.spawn(qk_gen_worker)] + [gevent.spawn(worker, str(i)) for i in range(worker_num)] 
    gevent.joinall(workers)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-s', '--start', dest='start_page',
                      type='int',
                      default=0,
                      help='start_page')
    parser.add_option('-e', '--end', dest='end_page',
                      type='int',
                      default=4,
                      help='end_page')
    parser.add_option('-w', '--worker', dest='worker_num',
                      type='int',
                      default=50,
                      help='worker_num')
    parser.add_option('-p', '--path', dest='dir_path',
                      default='/data/brand',
                      type='str',
                      help='dir_path')

    (options, args) = parser.parse_args()
    assert options.start_page >= 0
    assert options.end_page > 0
    assert options.worker_num > 0
    if options.start_page >= options.end_page:
        raise ValueError("start page must gt end page")
    if not os.path.exists(options.dir_path):
        raise ValueError("dir path not exist")
    dir_path = options.dir_path
    main(options.start_page, options.end_page, options.worker_num)
