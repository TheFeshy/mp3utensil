'''Test Module for mp3frame module'''

import unittest
from ctypes import c_uint32
import sys

import mp3frame
import mp3header

class Test_MP3Frame(unittest.TestCase):
    
    def setUp(self):
        #partialmp3_4k_64kb = b'\xff\xfbP\xc0\x00\x00\n\x81<\xf6\x196\x80\x01H\x16!C\xb0\x90\x00\xf08\x081o\x80\xc1\xc0\n\x1e\x1a\xa0R\x9e\x1213\xfcy\x8c\x01\xa7\xfa\x04\xb9|\x97\xff\xc6\x10z\x12\x83\xcd?\xff7\x18A\xc8hK\x92\x7f\xff\x92\xe5\xc2\xe1\xa2\x06f\xff\xff\xf9(\\4/\x97\xcd\xcc\t\x02\x87\xff\xff\xe5\xf2\xf9\xb8\xe4.1\xban\\9\xff\xf9@|\x08\x18\xca$<\xa0\x17C"*G\xd9\x19\xe4\xaaW"\xfc^\xe8K\xee\xefJn\xef\xff\xff\xae\x06.\xb3\xedz\x0cG\xc50\xf1\x9bR\xae&\xeb\xa8p\x8c\x83\xcf\x13\x99F\xaa\r\xd2oMb\x91\x87X\xc5\x8c\x18\x8e\xf5\x84\x85\x85\xb2H\x15)b\x90\xa5\xb1^\xb5\xa17Z\xd3\x89\xcadwe\x1c\x04\x8aNMr\xeaB\x9bQK\x91sq\x1c\x84\x10\xff\xfbR\xc0\n\x83\xcb\xd8\xb1\x08\x0cI\x89\x89C\x16a\x81\x86\xa507G\x00x\xc9\xc46\xae\x8a\x94:\xea4d\xfc!\xec\xdf\r;\x07\xdc\xdb\x11\xf2\x8d\x12\x0e\x0f\xab:=`\x9f8R7\xd2\x04|1\x14_u9BF\x87?m\x00\x87\x18G\x9f)\xc5o\x9d\xe9\xc2\xfdy\x1f\x8b\x19\xd2\xa3\xba3\x9f\xbf\xfd\xf7WK\xea\x10\x82\xc1\xd6\xd3JMv$\xe3\x03\xf0N\x14;\x80\xec\'"b>\x93j\xd4\xddD\xb3\xa8w\xf7\xa4S\xfe\x85O\xa7\xd50"S&Hl\x85\xbf\x02\xe8\xd4\xccX\x8b\xb5\xeac\xedz<f\x91\x10K\xfe\x88\xa2\\\xd0\x11C\xf23N\x92\xa69\xca.\x98\xd5\xc3\xb14\xce\x07\x80Z\'\x95N\x946R\x8f\x8f\x8f0Q\xaa\x1bph\xce\xf7\xef\x9bc\xf9\xf1\x12\xab\xfd\x8c\xff\xfbR\xc0\x10\x80\n\x00\xb1\x0c\x15\x95\x80\x01\xf7\x1ba\x030\xf0\x01\x7f/g\x0c \x91@\xbdQ\xfb\xa3\xfc\x0e\xa2M\xeca\'\x98c\n=\x01n\xe6\x80\xf5\x8c8\xc6\x11d\xf98\xa6\xe7R60\xe3E\x1e\xd3\xb1Fu\x0ct\x0e\x8fh\xc1\xca\xce"<W0\x85J\x0e\x99hpM\xe7\xf52\x9b\xd5f|\x9c\xb1\x1a\x94\xba\x18\x8f^8\x8f%\xe0\xefdnX\xba^\x1aWhFP\x19Q\xb1\xc7W\xa1JL\x17\xb5\x12\xb21\x8em\xa3\x18N\xb4*\x12)mE2)\xf2E.{\xb8)WG\n\xd2r\xfb8\xd3\x0eS\xe7u?\n4)\xcfw\xed\xa8J3\x18\xa6\xb1\xe9\xf5\xe9\x7f\n*\xc1\xd7\x962\xa1r\xf9\xfaw\x94\x7fM\xfcK\xf1\xff\x7f\x04\x80\xda\x10T}R\xc5kZ\xd2y5\xff\xfbR\xc0\x07\x83\xc9\xc4\xb9\x0c\x1c\xf4\x80\x01*\x17!\x80\xf5\xa50Zg\xaa\xaf\xc4\x05cy\xf9\x1b97{T\xa1\xcc\xa0D\x91\xfaN{\xd9\xa2\x00\xc3v)\xc5\t:\x00\x8c\x1b3*af\xda\xecJ\x14\x80M,8<\x17\x8e_\x83]\xad\x1c\x8b\xce\xae\xacC\xb4_\x16\xc6\xfc\xfcJ\x1cf\xa9\xea_\x17`\x0c1\x03\x82@<\x11g\xfb+\xd46\xaf\xe5\xb5\xb4j\xf5\x98Cab\xf3\x92S\xcf\xc9.\x06\xfc\xedw\xe4\xb2\xa4\xd0\xd2\xc6F\x1a\x1d\xe3V*\xc3P\xd8JH[\x87\xfc\x19\x9a\t\xaa\xce\\\x9az\xcb\xcb6kJ\xffg\xc0h\x08\xedS\x82\xc2\xbet\x98\xa2\xed\x14\xb0\xa6\x90\xfd\xfbQ\xf3\xaf\xfb{\xac\xcf\xaf\x8e\xc7g\x14\xb3\xf2-%6N\xf4\x9f\xbf\xb2\xd7\'\xd3-\xaa\x86\xd2]\xff\xfbR\xc0\x19\x03\xca\x10\xbf\x0e\x07\xbd)\x81J\x97\xe1\xc0\xf7\xa50l\xe5\x90`z$J\xa3%\x0b\xe0\xa5y\x7fi\x0f\x93\xe6\x88\xda(\x80P`\xa6\xcd\xfa\xd1b\\\x8d\xbc\xaa\xb8\r7.F\x0f\xb8/\xca\xf4\xc1\xa0\x86\xa3N\xcak0\xcc\x98\xbfWmq\xd2j\x9f\xe5\xeck\x8c\xf9\xfc\xf2\x8a\r\xfb\xebv\xc9\xa0"\x82\r\xa1*!1_\xe9\x9aj\x08\xd8x\x88{\xe9wVi@8\x15}\x10u\xc9\x1e:-z\x85P:\x93\'\x16\xbd5\xd5\x04\xc3sV\n\xd9A\xe2\xc6\x0bR8\xf8Ok\xba\xea\xe0@!\xb1\x82s7\xbb>\xed\xbe\xc3\x18\xb3\x97\xdd\xfdb\x95o~\xf5\xc9\xaf\x1bM\x84<nS\xea\x1be\xb1\xeb\x10\x18\xf2z_\xb9\'S\x8dv\xe5\xd9$S\xff\xde\xbe\xc3\xb4<dE\xff\xfbR\xc0%\x00\n\x84\xef\x1a\x060\xcb\x82\x93\xa1\xa5v\xb0\xf0\x01\xdc&\xc4\xf4\xb8\x9fS\x8ez\x8a\x06\x980\x14d\x89&@X\xaa\xd6\x85\xed\xddd \xe1\x91\xc1\x10[h\xa8\n\x03h\xf94Wy\x98+\x88$p\x02bC\xe9\x8c\xb7\xa5\x0bc\xf3\xf0\xe0x\xc0r\xa9\x8eu\xa5@\xf5\x93\xf8\xe7\xb20\x90\t\xa2\xa5>N\x10\xd5z\x1e\x9f3\x87\xe1p4\xc40\xe8\x99\xbd>u\xb1\xaa\xd9\x14nrD\xca\xbd\x0fQ\xae\x87\xac\xe3v\xe0\xa8\x81W\xec\xc8z\x1f\x8c0\x1c\x87\x03\xcc\x9b\x86#\x0b\xe5\xf6f\x08\x8cg\x02a\x0c4\x0f\xf3\x9cX\xd4s\xc6P\xaa\x8c\x83\xe9\x0f:\xd6\xcf\xc2V<\xd8\xdb\x9e+2\xffp\xe3\xdd\xfb\xcc\xbcx\x81\x90\xfe\x00\xa08J`\x95\x18G\x0b\xd3\xd4BU\xcc\xef\xff\xfbR\xc0\x06\x80\x0b\x99\x03L\x18\xf5\x80\x01\x7f\x1f\xe9\x0b\x1e\xd0\x00\xdc\x85\x98\xc9&i\x14"\x18\x15\x1b\x87\xe7\x15\x9a\x96\x9dA)A\x07\xa2L\xa5\xd6]\x96\xc5\xa7a\xaaH\xb5\xb1W\xf5\xf5\xaey\x14\x107\x9e=\xfd\x7f\x9a,l\x89$\xd98\xfe)\xbf\xb2\xd7\xa7\xb2\x14EE\x13\x8e\xbb\xb8\x88g0\xf8\x97[iu\x82B]\xfeYH%\x03 \x19\x1b\x1aX\xd0\xd8\r\xc5\xe1\x16\x0e1O\x01<*\x87\xe03\xce\xb1s#\xc3\xc8\xdeJ\x1b-\x03R\x9a)\xa9\x13d\r\x10:\x9af*N2\x10[\xa9i3\xa4\xa5\xeat\xfa\nH\xd5\xd5Zi=H\xd2t)\xad\x14\xba\x08\x1cgUjZj\xd6\xb4Z\xb6I\xd0\xfd\nV\xa9\t\x80E\xbc\xef\xa2\x85\x00\x00[m\xc4\xe3.\xca\x00\x98\xa7V\xff\xfbR\xc0\x06\x00\x0b\xa1-T\xf9\x83\x80\tx\x95\xeb\xeb0`\x00\xf6\xfc\xd9\x83[\xed\xdegp\xd8Q\x88\x02x\xb2\x9b\xc5i\xc8\x8e\x97d/\x8e2\x9c\x91\xc2+GG\x8d\xcd5\xca\xab\xef/C\x87R8\xb4\x98\xa6U\xec"\x88\xa0`\xdcN<\xd5\xedmT\xe5=\x0e}\x13sT\xa1\x9d\xe8\xa6\xf7\xd8y\x9d<\xc7\xf7M\xbf\x14;\x94\x00\x00\x00B\x06\xa2G]u\xdb\x00\x02\xf4\x12\xc0U\xe4\xc7,\xca>\xbb\x88H\x1fT<\x7f"\xb2\xa9\x85\xf1!\xcf\x81\xa1,U\x841\x11\xac\xd1\xbfre&\xde\x1f\x7f%\xb3=\x9f\xecCw\xe9)\xe3\xd1\x98C\x1f\xb5g\xa7\x99\xfc\xf9\'\x17\xf9\xfa\xfc\xe9\xe2V(\x10\x02\x18\x94\x08-\xabj\x98\x81|\x99\xef\x03*m6~\xdb_\xf8\x00\xa8\xb1\x8a\xba\x8c\xff\xfbR\xc0\x06\x00\x0b\xc4\xbf^y\x91\x80\tP\x92i\xcb\xb4\x80\x00\x87@XT\xbfc\x84%PI\x89\x9c$js\xa1\xd6P\x02\n\xc88\x99\xf1\xc2\x8aqj\xc2\x82\xda\xeat<\xac\xaax\x0b\xda\xc0\x7f\x07\x82,*^OA\x06\xbd8/\xe4\xc8\xb4\x0eR\x16L\xde\xee\xc2?\xf0ht\x9a\xbe\xf8\x1b\xcf\xa0\x07\xc1\xa0\xd1\xfe42;\xbf\x98\x82\r\x031\x00\x133\x0e\x14\\\xce\x17\x03\x9e\x01&9"K<a\x84\xa7\x98X\x99n\x84 \x86\x93O+t\xd0\xa842\xae\x9a\xf9\x8bf\xc5\x80p\x06=\x06T:\xedU\xfdW\xfb\xd4\xd4q\xe9\x04\rR\xe8\xc0\xb8;XY\x87\xfa\xd2\xc0\xb0\x10H\xad\x02P\x91\x8anf\xaa\xea\x00\x00\x088Bw\x8ah\x04U-\xa1P\x00s\xed\x84\xdc\xea\x8f\xb0\xff\xfbR\xc0\n\x82\n /UM`\xc4\xc9M\x1f\xea\xde\xb4P\x01\xb3\xdb\x19\x8a\xe5\x1a\x96\x1eP\x08;>\x94\xa0\x01U\xbe\x11VB\x87c\x7f\xa4\xfc0\xa7A\xef4\xaa`At\x9e\xfe\x03\xc6\x11/\xf4{$\xdb\xf3\x1d\xff\xff\xa1\xa3\xde^\x05\xff\x9c\xef/@\x0e\xdb\x12\x8c\x84\xb0\x10\xe40`\x05+\x18\\(\x1c5\xb2\xd7,\xca\x15\x1c\xa9\x12\x05C\x86\xe2\xf6\xe6\xc3\\=A\xed\x14\x9b\x1e\xc3\x0e`\xa1A!w3!\xfc\x9dV\xaa\x96T\xd6\xbb\x18\xac\xcc\xf7mH\xa8\xe8W~\xa52\x19$s\x1e\xbf\xfeQ\xe40\xab\x85\x96\xcf\xfe\xbdr\x90j\x00\x00\x00\xf8\x03\x03X9&s\x0b\x1c7O\xa0\t\xc8\x02H\xd7R\xcc\x18\xac\xc2\xcb\x90`\xd4\x01\x82\x02\xccA\xd9\xe10i\xd2`3\x01\xaeh\xff\xfbR\xc0\x16\x00\x10\x10\xddHY\xb6\x00\x01M )\xcf\xb4P\x01E\xa3RQW\xc5\xe9\xcf\x8b%vD\xe6P\xeeN&\xb5Q\xc6\xc6\x92H\x1e\xdf\xce\xb6\xdc\xe3ff>\xac\xc9.\x99u\xc7\xe5\xe9\xbfu\xd7\xc1=K\xacu\xc35\x7fX\xcd\x169\x14\xde\xee\xb4`\x91_E\xd1\xd2gmI\xe8Z\xa0@\xb8r]\xea\x05z\xcc\x87\xc1\'R\xb1p@\x01`/)\x887*\x1b\xac\xa1\xce\xe2\x80SU}\xee\x19e\x8c\xf8t\xc97\x06[-\xa3*9C\x92\xb2\xa5YJT\x87\x86\x18|\xba\xe5:\xff\x1dVms\xd1\xc8\x854\x12"<\xcc.\xaeR\xb2\xb1\x13D{2*\xb5\xaf\xff\xa8\xd10\xb2\x0f\xc5:}TZ\xccv\x05\x00\x1c\x02\xccl\xcd!"\xae\xe8\x19iC\xc3\x9b\xaa\xea\xa4z\xff\xfbR\xc0\n\x02\nH\xf3NmH\xeb\x89N\x9fj\x9e\xb2\x80\x01\x1f\xd2\x90\x8c\xc0VH(qcH\xcc\x92\xba~\xf7u \xb4\x8d\r\xd04n\xb5j\x8f\xf8\xf9\xa7\x9fs\x1fS(a\xae,\x14\x08\xa11\xe7\x8f\x8d\xd4\x9b\x8f\xb4\xc3\x1f\xfd\xcd2\xbf\xff9ThX\x0e\xd1D\x1b\x00^\x05\x9aa\xde\x92I-(_\xc7\xa6\x0e\xc3\x96\xad\xbf2\xdb\xda\x98\x15\x13\xd3[ZE\xd4ql\xe2\xa2\xc2\x0b\xcasu\x15\xff7\x115?}\xc7\xcd\xc4D\xe2\x15\xb8Br:+m\xf3j\xefU\xfe\xb5(:\xd5\xb4\xbf\xed\xad\xbbG\x1e\xc2(\xe1\xda\x07\xb8\x10v\xb7\x00\x00\x00\x90\x06\x00\x00\x00\x80\xb4\x00\x15\x18aH\x1e\x92-\xa5\x0b\xabz\xf6}\xd7#U\xa6>\xddgO9\xacV\x05aK\x88,\xb5\xd5\xff\xfbR\xc0\x15\x00\x0f\xb9\x1fUY\x87\x80\tR\x1fl7\x8a`\x01?\x8f\x8d\xfb\xed\xc1\xb2\x03\x0eaxt\x89\xf1\x15\xfb\xeck_^M\xb0R\x9a\xec\x10+F\xe4b\x81Y\xf5Y\xd4rU\xed^\xb7\xb8\xb1\xbc=\xd4\x87!\xe8C\xd8\x9a\xde\xc9}__w\x8f\x89s\xef\xaf\x98{\xd3\x1b\xecc\x1b\xdd\xf7\xf7\xff\xff\xcd;#\xe7\x0b\xceC\xe4\x80$\xa5tH\x82\x00\x00\x17\x84$\x16R\xb0\xb3\xab+\xea\xd5\xa6\x9f[\xb5z\xf7\xbd\xb4\xfbz3\xdd\xado\x18\xef\x7f\xfe\xff\xf6\xd8\xefm\x8ewe\x1e\xb0\x88\x1a).\xe2P!`\xf2H\xf5\x84\xa9\xc7%.\x8e\xceW\xa7x\xdc\x87\xdf}\xe3\xdb"\xda\xb4\x0e\x9bGi\x1ft\xc5\xbfH\xd5\xd7a\xa1p\x00\x00\x01\xe0\xa08-jRW\xf0\x88\xfa\xa3\x89\xff\xfbR\xc0\t\x80\x8a\x88\xf3a\xa4\x15\x0b\x89J\xa1\xac4!\xa1q9\x8ed\xff#2(\xa8@\x86\x11#\xb8\xea1o\xde\xbef/\xf8\xa3Na\x08tA\x82\xee\x10\x8b\n\xb1\xcc\x1d1\xd6\xad. \x94;ibu\xb7\xbe\xd9b\x9aw\xfe\x92\r\x12\xd1\x9e\x14\x1c\xe6U\x7f\xe1\x8c\xd1\xbf\xdf\xfe\xdb`N(+R\xe6K\x7f\xdd\xd5:\xb5\xd2O\xfe\x1e\x0e*\xb0C\x9b\x88\x9a\xfe\xff\xb8\'\x8a\xe2`<\xb2\xc4!PpT\x8aS\xcf8\xa1;\xd0~\xb64d\xde9\x1e\xa6\xee\xd9\xc7\xe6\xcb\x9f\xd5\xef_NE\x15\x8dD\xaeE\xb9:\xe1yV\xd2\x8eHY\xee@\xff\xff\xb2Q\x00\x00\x01\xf1`\xc6!#\xb9\xfa\xcaz\xb2\x80\x1dI]^Xa\x02e)]\xa5\xff\xf4\x9f\x8e\xd4y\xa4\xc4\x98[\x86\xff\xfbR\xc0\x14\x02\n-)]\xa0\x89\x0b\xc94\x99\xea\xf41\x99q\x18, \x87\xc2\xea6\t$T\xd1a\xb8\xc8\x17\xb0*\xda\x05jD^\xd9\xad)k\x8b\x1d\xf7\xcf5U\x1f\x93z\xd7\xfc\x7f\x7f\x03\xf2\xd6\xb4@ \x018\xc8KP\xc7\x0e\x19|\xa4R\x19k\xcb\xfd\xf7\x94S0\xa7[\x1b\x19\xd9\xeb\xef\xff\xff\xf3\xb4\xb3\xb1\xdau\x0eN\xc9\x01\x8dJd\x8e\x95b\x0b5.K\x01\x92\xc3\x95ME\xcb\x9eeA+\xbc_\xc88b\xf8<\xa3\xe0\xaf\xaf\x7f\xb2\x0b\xaa\x97i3@\x00\x00\x00\xd1\x04\x06Na\x83g\x98\xbb\x8d\xa4f\x7f\xb1\xcf\xbfs\xf2\xc4\xe6`\xd3%\x89\xa5*Y\xa9e\\\xb25\xb9\xff\xb8\xe5\xec|\x91O61\x10\xb6K\xa2\x92[f,\xabSI\xa4\xc5*\x05\x81\x10\x02\x08\x85\xff\xfbR\xc0"\x80\x0c\x88\xfbA\xb4\x84\x80\nM"\xe2\xc30\xf0\x00OJ\xc9Um\x86\xed\x0b\xad\t\x0bV\xca\xa4\xb5\xef)f\xbf\xf6\xab\xb14\x14\xd6\xdd\xff\xd8_\xca\x01I%@\x84\xe5\x9a\xd1\xd5.{\xa3\xbbG\xc6\r\x07\xccH\xe6"\x87R\xa5\xfc\x15l\xe9\xd5\xc0\x04\xd3\x19\xe7{\xd5r\xe4\n\xc5\xbdPKE\xa0\xab@\'\xde\xa9\xeb:\x0b&Z\x1e\x90\x88}J\xc4\xe4\xfa\x14\t\\IP\xf9(\x0f1rB\xd0\x95\xb8c\xe4\x9c\x90\x94\xed\x9e"r\xf4p(N\xf0f\x1d\xb2\xae\xcd\xa30\x87\x8fV\x99\x99bD>NU\x8d\xae\x86\xba\xbc\x91\x1e\xe5*\x11\t\x9c\xc9T!m\x8d)\xd6\x8f\x06\xb3@D\xef\xc5\xf8\x84IW2=\xae\xf1\xfe:\xeb&:\xc1*k\xcd\t& J\x12J\x99\xff\xfbR\xc0\x04\x81\xc9\xf0\xd1\x10\x1c\xb4\x80\x01;\x9a"\xd5\x97\x89p\xe7\xd2\x10\x89DE\x8b\x08\xc3\xde\xbfH\x97w\xf4B\x81.\x95\x94E(\x06\xdf\xc2wj"e\x82\x13)\x1e3\xfa\xa8\xef3\xff\xd7t\x99T\xcc\x8d\x7f\xbf\xack$4\xa0\xa4lC\x10\xb2\xbe\xeb\xff\x97\xfe\xc86/\xda\xa1\xcf\xebn\x80e\x8a\x92NYB\xe2\x05\x082\x947"6\x86\x07\x0e^5\xd6\xbb/Bi\x15\x1e_\xc5\xb0[\x0e\x02\xe0\x86,nKS\xfc8\xea\x8c\xb3b\x04\x0e\xe3\x16xq\xc8\x02\xc81\x05\x9cI\xac9\x96\xaf\x87\n\xca\xd3M\xd0(\xe2\xb3\x18\x1a\x18\xce\x9f\xaf\xc3r\x95\x08\n\x00\x00#\xf8\x8c\x04\xd4\xcf\xcc\x0c@\xb6\xe0\x91\x01#u\x02\x04\xc4\x9d\x08\x83bA3K00D\xd5\x91,Z\xa7@\xff\xfbR\xc0\x13\x00\x0b\xf8\xe5\x1e\x95\xb5\x80\t\xd9\x1a(w6\xf0\x01l\x85>"\xac\t%C\xb4\xb1S\xc6J\xd3\x88ETR\x0e>\\v\xdb]\xac\xda\x8a|28c\xa6\x9f/\xb6O\xf7_7\xd4S?\xfd\xec\xfe%\x9f_\xcd\xfe\xc6K\x10v\xd3\x87\xd5\x00\x00\x00@\x10(\x14\n\x15NI[\xb2\x00\x1a:\xbb1#"\xe4\x18\xa51\x90\x07\xb2u4d\r\xaa\x12\x9d\xd7e\xc7\x83\x1c\xa7\x8b\x12X\xc2\xf1\x89\xc2\xa2\x06\x02"\xb5\xf5qx\xdb2\xcb\xc6c\xd3\x19\xaf\xfa\xdbz\xae\xea5\xbc\xe6\xbf\xdbt\x93=\xfc\x7f\xbb\xe7\xea\xbf;\xcf\xa6\xef\x87\x9a\xfe\x94{\x8d|c\xfc\xe7\xfd\xe2=\xa9\x1f\x89\x11\x14\xcb\xea^\x7f}b\xdb\xff\xdak\xbf\xfe\x12\xe8\xa5\x00\x00\x0c\x00\n&2)\x18\xf4\xb7\xd3\xff\xfbR\xc0\x06\x03\x0b\xb1\x1d6}\xc2\x80\tD\xa3\'\xce\xb6P\x01\x17\x14L\x989+@\xa4\xd0p\xfeR\xe3*U\xb4,\x01\x7f\x141\xae\xca\x14\xe0\x05\x0f\xd5\xcaU\n\x01\x0cfRRP9\x8av\xae\x8d\xd5\xc2\x83\xc2\x82,\xaedK\x0b9F\x8c\x12:8\xe5\x1c\xe7\x14\x18S\xba\xff\xde\xae\x84I\xd1\x7f\xff\xfe\xc6\xf6\xc6\x98r\xcc>\xb4@\x02P\x01\x00\xc1`\x13\xc8\xda\x19\x161"\xc1+53\x12\rf\xf5Y[s\x1a3\x9b\x91Hi\x9a\xf9\x02\xc9\x15\x89\xb4\xedigd!Pz\xbd\x7f\xa2\x1cU16E\xb3\xaaG:\xb7\xb5N\x89\xff\xd6\xb8\x0eQqC\x10\xe7\x7f\xff\xeay\xbf\xd5\x8a**\x0b\x8a\x00\x00\x00B\xa0\x08\x00\x00\x81\xad\x00\x0c\xb5(\xe3\x14\x8c\xc7,\xcf\x0c\xcb\x1f\xe0\xd3\xff\xfbR\xc0\x0c\x80\r-!EY\xb5\x00\x01\x84\x18\xe8\xd76`\x00\x12!p\x10\x188QLF\x83\x81E*]8\xa6\x0e\x80p\x03\xb85\x1d\x1f\x18\n\xc6\xe4\x88\xc6\x98aq\xe1\x05N<\xe9\x1a\xb5\xfd\x97v\xbc\xd7G9\x8fgVWE\xcfVD=\xfbL\xf3\x90\xd6\xf7$\xfc\xc3L\xfe\xcd\xfa\xa5\t\x0c;\xe6\xf3\xc9\xcb6\xfa\xc2\x00\x00<\xc7\xd0e\xc3g\x02|e\x18\x86\xb2>`yF\xbc\x0c\x10\x1a\x02\x07H'
        pass
    
    def test_short_init(self):
        h = mp3header.Header_struct()
        h.d = int.from_bytes((0xFF,0xFA,0xA9,0x0F), sys.byteorder)
        frame = mp3frame.MP3Frame(h, 0)
        self.assertEqual(frame.length, 720)
        h.d = int.from_bytes((0xFF,0xFA,0x51,0x0F), sys.byteorder)
        frame = mp3frame.MP3Frame(h, 0)
        self.assertEqual(frame.length, 208)





