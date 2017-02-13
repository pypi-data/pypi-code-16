import Python.brackets_cutter.core
import unittest


class KnownResults(unittest.TestCase):
    known_res = (('', ''),
                 ('((((((((((((((((((((', ''),
                 (':)))))))))))))))))))', ':)))))))))))))))))))'),
                 ('()()()()()()()()()((', '()()()()()()()()()'),
                 ('esdfd((esdf)(esdf', 'esdfd((esdf)'),
                 ('j(n)(oxq(og(w(xo)s()', 'j(n)(oxq(og(w(xo)s()'),
                 ('bxq(cowpnnpxunl((ubm', 'bxq'),
                 ('odrko(jur(b((mzw)r))', 'odrko(jur(b((mzw)r))'),
                 ('((tqtaak)()i)esyz)ah', '((tqtaak)()i)esyz)ah'),
                 ('xm(mmsm)xvha(sno(n()', 'xm(mmsm)xvha(sno(n()'),
                 ('szrkhd)ddk(e(obqsaq(', 'szrkhd)ddk'),
                 (')((g(wa)oo(ma())avkc', ')((g(wa)oo(ma())avkc'),
                 ('s(jigjq)jx(avydafw(j', 's(jigjq)jx'),
                 ('s)()r(x)))ra)aufcz((', 's)()r(x)))ra)aufcz'),
                 (')ylg(eczh(d)f(xbewcf', ')ylg(eczh(d)f'),
                 ('olxk))t(ut)ho(tf()(m', 'olxk))t(ut)ho(tf()'),
                 ('g(xzpd)v)rb((yads((c', 'g(xzpd)v)rb'),
                 ('nnbkl)jpk)h)c)dcw)ei', 'nnbkl)jpk)h)c)dcw)ei'),
                 ('byqs(ocnxc(hn(xwlhvs', 'byqs'),
                 ('yarkzxw()ptnb()h(y)g', 'yarkzxw()ptnb()h(y)g'),
                 ('(b(t)oebd))mi)(gcav(', '(b(t)oebd))mi)'),
                 ('ssbuazon((rs))ct(f()', 'ssbuazon((rs))ct(f()'),
                 (')fy))zc))e()chzup()d', ')fy))zc))e()chzup()d'),
                 ('e))ph(n)fn)a)wuwiygw', 'e))ph(n)fn)a)wuwiygw'),
                 ('jys)h(p)(nwa)udgma))', 'jys)h(p)(nwa)udgma))'),
                 ('skmoqrk)(d)sr)rdby(u', 'skmoqrk)(d)sr)rdby'),
                 ('((j()op(lwqp(sz(ed)k', '((j()op(lwqp(sz(ed)k'),
                 ('aee)r(mmo)oxz(qu)bgo', 'aee)r(mmo)oxz(qu)bgo'),
                 ('n)l(r()(((cfozautz((', 'n)l(r()'),
                 ('n(gpu))()()x)p(yhbab', 'n(gpu))()()x)p'),
                 ('(khnvbct)n)r(vx(z)bu', '(khnvbct)n)r(vx(z)bu'),
                 ('m)hj(gh()(wf((oxceew', 'm)hj(gh()'),
                 ('lbv)er(w(u()oaigi((v', 'lbv)er(w(u()oaigi'),
                 ('vu(vp)qa()acsb)bl(e)', 'vu(vp)qa()acsb)bl(e)'),
                 ('zkunaot(jl(r)c)(w()(', 'zkunaot(jl(r)c)(w()'),
                 ('o)dw)q((nm)d()l)yx(k', 'o)dw)q((nm)d()l)yx'),
                 ('y(wlkjpr)))(u))q(ry)', 'y(wlkjpr)))(u))q(ry)'),
                 (')u(ljr(u(hggy(k)g(f(', ')u(ljr(u(hggy(k)g'),
                 ('ekvhn(ind(sxnapj(rq)', 'ekvhn(ind(sxnapj(rq)'),
                 ('o((cu(vcf(idadni))(s', 'o((cu(vcf(idadni))'),
                 ('(b(gtvqaip(ve)j(wy(l', '(b(gtvqaip(ve)j'),
                 ('(fxfrw(k)hgfihrv)((x', '(fxfrw(k)hgfihrv)'),
                 (')u()cgvhow((sol)oo(l', ')u()cgvhow((sol)oo'),
                 ('(fr(md)puyob)veznb(h', '(fr(md)puyob)veznb'),
                 ('(mglotvoo)w)))mbjjse', '(mglotvoo)w)))mbjjse'),
                 ('()wn()q((x((msw)qp)w', '()wn()q((x((msw)qp)w'),
                 ('pw(pa(eu(i)(((eznn(e', 'pw(pa(eu(i)'),
                 ('k(aiwh)v)o)jxtemafhh', 'k(aiwh)v)o)jxtemafhh'),
                 ('y)fpboavfhc(liht(un(', 'y)fpboavfhc'),
                 ('eqoa)gnka)yhm)f(bhxf', 'eqoa)gnka)yhm)f'),
                 ('jyzjvtwhcfqduhhi()g)', 'jyzjvtwhcfqduhhi()g)'),
                 ('i(g(a(cdng(hxrlh(u)i', 'i(g(a(cdng(hxrlh(u)i'),
                 ('t)oel(ean)hfl(azjjd)', 't)oel(ean)hfl(azjjd)'),
                 ('lyw(ch(s)hr(pb)(kuuz', 'lyw(ch(s)hr(pb)'),
                 ('dy(ozby)rqi)g((fh(rj', 'dy(ozby)rqi)g'),
                 ('(lhk(m)(j(()k(nnfn((', '(lhk(m)(j(()k'),
                 ('ut)b(xa)u(ctq)hra)))', 'ut)b(xa)u(ctq)hra)))'),
                 ('f(pu()su()ds)nvkp()r', 'f(pu()su()ds)nvkp()r'),
                 ('c(o(t)nqb(o(f)ufg)q(', 'c(o(t)nqb(o(f)ufg)q'),
                 ('n)f(xukmiyb)oimwds((', 'n)f(xukmiyb)oimwds'),
                 (')(sfkiaiibwp))albhpj', ')(sfkiaiibwp))albhpj'))

    def test_regexp_solution_known_res(self):
        for input_str, output_str in self.known_res:
            result = Python.brackets_cutter.core.cut_unclosed_brackets(input_str)
            self.assertEqual(output_str, result)

    def test_without_regexp_solution_known_res(self):
        for input_str, output_str in self.known_res:
            result = Python.brackets_cutter.core.cut_unclosed_brackets_regexp(input_str)
            self.assertEqual(output_str, result)


if __name__ == '__main__':
    unittest.main()
