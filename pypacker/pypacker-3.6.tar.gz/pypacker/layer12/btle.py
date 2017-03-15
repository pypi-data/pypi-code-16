"""
Bluetooth Low Energy

https://www.bluetooth.com/specifications/adopted-specifications
https://developer.bluetooth.org/TechnologyOverview/Pages/BLE.aspx
https://developer.bluetooth.org/TechnologyOverview/Pages/LE-Security.aspx
"""

# TODO: implement PDU types
# TODO: add tests


from pypacker import pypacker
from pypacker import triggerlist

import logging
import struct

# avoid unneeded references for performance reasons
pack = struct.pack
unpack = struct.unpack
unpack_byte = struct.Struct(b"B").unpack

logger = logging.getLogger("pypacker")

"""
flags as BE (in packet: as LE), 0x0001 becomes 0x0100
0x0001 indicates the LE Packet is de-whitened
0x0002 indicates the Signal Power field is valid
0x0004 indicates the Noise Power field is valid
0x0008 indicates the LE Packet is decrypted
0x0010 indicates the Reference Access Address is valid and led to this packet being captured
0x0020 indicates the Access Address Offenses field contains valid data
0x0040 indicates the RF Channel field is subject to aliasing
0x0400 indicates the CRC portion of the LE Packet was checked
0x0800 indicates the CRC portion of the LE Packet passed its check
0x1000 indicates the MIC portion of the decrypted LE Packet was checked
0x2000 indicates the MIC portion of the decrypted LE Packet passed its check
"""

_WHITE_MASK			= (0x0100, 8)
_SIG_MASK			= (0x0200, 9)
_NOISE_MASK			= (0x0400, 10)
_DECR_MASK			= (0x0800, 11)
_REF_ACC_MASK		= (0x1000, 12)
_OFFENSE_MASK		= (0x2000, 13)
_CHAN_ALIAS_MASK	= (0x4000, 14)
_CRC_CHECK_MASK		= (0x0004, 2)
_CRC_PASS_MASK		= (0x0008, 3)
_MIC_CHECK_MASK		= (0x0010, 4)
_MIC_PASS_MASK		= (0x0020, 5)

# TODO: make this more generic
FLAGS_NAME_MASK = {
	"whitening": _WHITE_MASK,
	"sigvalid": _SIG_MASK,
	"noisevalid": _NOISE_MASK,
	"decrypted": _DECR_MASK,
	"refaccvalid": _REF_ACC_MASK,
	"offenses": _OFFENSE_MASK,
	"chanalias": _CHAN_ALIAS_MASK,
	"crcchecked": _CRC_CHECK_MASK,
	"crcpass": _CRC_PASS_MASK,
	"micchecked": _MIC_CHECK_MASK,
	"micpass": _MIC_PASS_MASK
}

BTLE_HANDLE_TYPE	= 0

_subheader_properties = []

# set properties to access flags
for name, mask_off in FLAGS_NAME_MASK.items():
	subheader = [
		name,
		(lambda mask, off: (lambda _obj: (_obj.__getattribute__("flags") & mask) >> off))(mask_off[0], mask_off[1]),
		(lambda mask, off: (lambda _obj, _val: _obj.__setattr__("flags", (_obj.__getattribute__("flags") & ~mask)
																| (_val << off))(mask_off[0], mask_off[1])))
	]
	_subheader_properties.append(subheader)


class AdvData(pypacker.Packet):
	__hdr__ = (
		("len", "B", 0),
		("type", "B", 0)
	)


def parse_advdata(bts):
	off = 0
	ret = []

	while off < len(bts):
		alen = bts[off]
		pkt = AdvData(len=alen, type=bts[off + 1], body_bytes=bts[off + 2, off + 2 + alen])
		ret.append(pkt)
		off += alen + 1
	return ret


# BTLE packet header
# http://www.tcpdump.org/linktypes.html -> LINKTYPE_BLUETOOTH_LE_LL_WITH_PHDR
class BTLEPhdr(pypacker.Packet):
	__hdr__ = (
		("channel", "B", 0),
		("signal", "B", 0),
		("noise", "B", 0),
		("aaoffense", "B", None),
		("refaddr", "4s", b"\xFF" * 4),
		("flags", "H", 0),
	)

	__hdr_sub__ = _subheader_properties

	def _dissect(self, buf):
		self._init_handler(BTLE_HANDLE_TYPE, buf[10:])
		#logger.debug(adding %d flags" % len(self.flags))
		return 10

#
# Sub header
#


class AdvInd(pypacker.Packet):
	__hdr__ = (
		("adv_addr", "6s", b"\xFF" * 6),
		("adv_data", None, AdvData),
	)

	def _dissect(self, buf):
		parse_advdata
		self._init_triggerlist("adv_data", buf[6:], parse_advdata)
		return len(buf)


class AdvNonconnInd(pypacker.Packet):
	__hdr__ = (
		("adv_daddr", "6s", b"\xFF" * 6),
		("adv_data", None, AdvData)
	)

	def _dissect(self, buf):
		self._init_triggerlist("adv_data", buf[6:], parse_advdata)
		return len(buf)


class ScanRequest(pypacker.Packet):
	__hdr__ = (
		("scanaddr", "6s", b"\xFF" * 6),
		("advdaddr", "6s", b"\xFF" * 6),
	)


class ScanResponse(pypacker.Packet):
	__hdr__ = (
		("adv_daddr", "6s", b"\xFF" * 6),
		("adv_data", None, AdvData)
	)

	def _dissect(self, buf):
		self._init_triggerlist("adv_data", buf[6:], parse_advdata)
		return len(buf)


class ConnRequest(pypacker.Packet):
	__hdr__ = (
		("init_addr", "6s", b"\xFF" * 6),
		("adv_addr", "6s", b"\xFF" * 6),
		("access_daddr", "4s", b"\xFF" * 6),
		("crcinit", "3s", b"\xFF" * 3),
		("winsize", "B", 0),
		("winoff", "H", 0),
		("interval", "H", 0),
		("latency", "H", 0),
		("timeout", "H", 0),
		("chanmap", "5s", b"\xFF" * 5),
		("hop_sleep", "B", 0)
	)

#
# Data packets
#


class DataLLID0(pypacker.Packet):
	pass


class DataLLID1(pypacker.Packet):
	pass


class DataLLID2(pypacker.Packet):
	__hdr__ = (
		("len", "H", 0),
		("type", "H", 0)
	)


# LLX-packets
class LLEncReq(pypacker.Packet):
	__hdr__ = (
		("rand", "8s", 0),
		("encrdiv", "H", 0),
		("masterdiv", "Q", 0),
		("masterinit", "I", 0)
	)


class LLEncResp(pypacker.Packet):
	__hdr__ = (
		("slavediv", "8s", 0),
		("slaveinit", "I", 0)
	)


class LLStartEnc(pypacker.Packet):
	pass


class LLVersionInd(pypacker.Packet):
	__hdr__ = (
		("version", "B", 0),
		("company", "H", 0),
		("subcompany", "H", 0)
	)


class DataLLID3(pypacker.Packet):
	__hdr__ = (
		("opcode", "B", 0),
	)

	def _dissect(self, buf):
		self._init_handler(buf[0], buf[1:])
		return 1


pypacker.Packet.load_handler(DataLLID3,
	{
		LLID3_ENCREQ: LLEncReq,
		LLID3_ENCRESP: LLEncResp,
		LLID3_STARTENC: LLStartEnc,
		LLID3_VERSIONIND: LLVersionInd,
	}
)


#
# Base header
#


"""
Spec 4.0, p2203

0000 ADV_IND
0001 ADV_DIRECT_IND
0010 ADV_NONCONN_IND
0011 SCAN_REQ
0100 SCAN_RSP
0101 CONNECT_REQ
0110 ADV_SCAN_IND
0111-1111 Reserved

"""
PDU_TYPE_ADV_IND			= 0
PDU_TYPE_ADV_DIRECT_IND			= 1
PDU_TYPE_ADV_NONCONN_IND		= 2
# SCAN_REQ?
PDU_TYPE_SCAN_RSP			= 4
PDU_TYPE_CONNECT_REQ			= 5
PDU_TYPE_ADV_SCAN_IND			= 6

PDU_TYPE_DATA_LLID0			= 0
PDU_TYPE_DATA_LLID1			= 2
PDU_TYPE_DATA_LLID2			= 3
PDU_TYPE_DATA_LLID3			= 4


def _get_property_subtype_get(obj):
	if obj.access_addr == b"\xD6\xBE\x89\x8E":
		return obj.info & 0x0F
	else:
		return obj.info & 0x03


def _get_property_subtype_set(obj, val):
	if obj.access_addr == b"\xD6\xBE\x89\x8E":
		obj.info = (obj.info & ~0x0F) | val
	else:
		obj.info = (obj.info & ~0x03) | val


_subheader_btle_properties = [
	["pdutype",
	lambda _obj: _get_property_subtype_get(_obj),
	lambda _obj, _val: _get_property_subtype_set(_obj)],
	["random_rx",
	lambda _obj: (_obj.info & 0x80) >> 7,
	lambda _obj, _val: (_obj.info & ~0x80) | (val << 7)],
	["random_tx",
	lambda _obj: (_obj.info & 0x40) >> 6,
	lambda _obj, _val: (_obj.info & ~0x40) | (val << 6)],
	["llid",
	lambda _obj: _obj.info & 0x03,
	lambda _obj, _val: (_obj.info & ~0x03) | val],
	["is_adv",
	lambda _obj: _obj.access_addr == b"\xD6\xBE\x89\x8E"]
]


class BTLE(pypacker.Packet):
	__hdr__ = (
		("access_addr", "4s", b"\xff" * 4),
		("info", "B", 0),
		("len", "B", 0),
	)

	__hdr_sub__ = _subheader_btle_properties

	def _dissect(self, buf):
		hlen = 8

		if buf[: 4] == b"\xD6\xBE\x89\x8E":
			# logger.debug("got ADV... packet")
			btle_type = buf[4] & 0x0F
		else:
			# logger.debug("got data packet")
			# max value is 15, shift to avoid collision with ADV... packets
			btle_type = (buf[4] & 0x03) << 4
		logger.warning(">>>>>>>>>>>> unpacked type: %r" % btle_type)
		self._init_handler(btle_type, buf[hlen: -3])

		self._crc = buf[-3:]
		return hlen

	def bin(self, update_auto_fields=True):
		"""Custom bin(): handle crc for BTLE."""
		return pypacker.Packet.bin(self, update_auto_fields=update_auto_fields) + self.crc

	def __len__(self):
		return super().__len__() + len(self.crc)

	# handle crc attribute
	def __get_crc(self):
		try:
			return self._crc
		except AttributeError:
			return b""

	def __set_crc(self, crc):
		self._crc = crc

	crc = property(__get_crc, __set_crc)


# BTLE is the only handler for BTLEPhdr
pypacker.Packet.load_handler(BTLEPhdr,
	{
		BTLE_HANDLE_TYPE: BTLE
	}
)

pypacker.Packet.load_handler(BTLE,
	{
		PDU_TYPE_ADV_IND: AdvInd,
		PDU_TYPE_ADV_SCAN_IND: ScanRequest,
		PDU_TYPE_ADV_NONCONN_IND: AdvNonconnInd,
		PDU_TYPE_SCAN_RSP: ScanResponse,
		PDU_TYPE_CONNECT_REQ: ConnRequest,
		PDU_TYPE_DATA_LLID0 << 4: DataLLID0,
		PDU_TYPE_DATA_LLID1 << 4: DataLLID1,
		PDU_TYPE_DATA_LLID2 << 4: DataLLID2,
		PDU_TYPE_DATA_LLID3 << 4: DataLLID3,
	}
)


def decrypt_btle(packets, callback_decrypted=lambda p: p):
	logger.warning("trying to decrypt BTLE")

	# target AA (non ADV) -> [ltk, ia, iastate, ra, raste]
	# TK -> STK -> LTK
	# pcap decrypting: non empty PDU ->
	AA__ltk_ia_iastate_ra_rastate = {}

	for pkt in packets:
		pkt = pkt.upper_layer

		if pkt.is_adv and pkt.pdutype == PDU_TYPE_CONNECT_REQ:
			# logger.debug("got PDU_TYPE_CONNECT_REQ")
			# TODO: prop for rx_random tx_random
			AA__ltk_ia_iastate_ra_rastate[pkt.access_daddr] = [None,
									pkt.init_addr,
									pkt.rx_random,
									pkt.adv_addr,
									pkt.tx_random]

		if not pkt.is_adv:
			# logger.debug("got data packet")

			if pkt.llid == 2:
				# logger.debug("got llid==2")

				if pkt.type == 0x0600:
					# logger.debug("got CID==6")

					if pkt.body_bytes[-1] == 0x01:
						prequest = b"XXX"
						pass
					elif pkt.body_bytes[-1] == 0x02:
						presponse = b"XXX"
					elif pkt.body_bytes[-1] == 0x03:
						pconfirm = b"XXX"
					elif pkt.body_bytes[-1] == 0x04:
						prandom = b"XXX"
			elif pkt.llid == 3:
				# logger.debug("got llid=3")

				if pkt.opcode == 0x03:  # LL_ENC_REQ
					rand = b"XXX"
					ediv = b"XXX"
					skdm = b"XXX"
					ivm = b"XXX"
				elif pkt.opcode == 0x04:  # LL_ENC_RESP
					skds = b"XXX"
					ivs = b "XXX"

"""
SKD = SKDm || SKDs [pg 2247] = skds + skdm
sesion key = e(STK, SKD)
	aes_block(state->stk, skd, state->session_key);


void calc_iv(crackle_state_t *state) {
	assert(state != NULL);

	copy_reverse(state->ivm, state->iv + 0, 4);
	copy_reverse(state->ivs, state->iv + 4, 4);
}

void calc_confirm(crackle_state_t *state, int master, uint32_t numeric_key, uint8_t *out) {
    int i;
    uint8_t p1[16] = { 0, };
    uint8_t p2[16] = { 0, };
    uint8_t key[16] = { 0, };
    uint8_t *rand = master ? state->mrand : state->srand;

    numeric_key = htobe32(numeric_key);
    memcpy(&key[12], &numeric_key, 4);

    // p1 = pres || preq || rat || iat
    memcpy(p1 +  0, state->pres, 7);
    memcpy(p1 +  7, state->preq, 7);
    p1[14] = state->rat;
    p1[15] = state->iat;

    // p2 = padding || ia || ra
    memcpy(p2 +  4, state->ia, 6);
    memcpy(p2 + 10, state->ra, 6);

    for (i = 0; i < 16; ++i)
        p1[i] ^= rand[i];

    aes_block(key, p1, out);

    for (i = 0; i < 16; ++i)
        p1[i] = out[i] ^ p2[i];

    aes_block(key, p1, out);
}void calc_confirm(crackle_state_t *state, int master, uint32_t numeric_key, uint8_t *out) {
    int i;
    uint8_t p1[16] = { 0, };
    uint8_t p2[16] = { 0, };
    uint8_t key[16] = { 0, };
    uint8_t *rand = master ? state->mrand : state->srand;

    numeric_key = htobe32(numeric_key);
    memcpy(&key[12], &numeric_key, 4);

    // p1 = pres || preq || rat || iat
    memcpy(p1 +  0, state->pres, 7);
    memcpy(p1 +  7, state->preq, 7);
    p1[14] = state->rat;
    p1[15] = state->iat;

    // p2 = padding || ia || ra
    memcpy(p2 +  4, state->ia, 6);
    memcpy(p2 + 10, state->ra, 6);

    for (i = 0; i < 16; ++i)
        p1[i] ^= rand[i];

    aes_block(key, p1, out);

    for (i = 0; i < 16; ++i)
        p1[i] = out[i] ^ p2[i];

    aes_block(key, p1, out);
}


void calc_stk(crackle_state_t *state, uint32_t numeric_key) {
    uint8_t rand[16];

    assert(state != NULL);

    // calculate TK
    numeric_key = htobe32(numeric_key);
    memcpy(&state->tk[12], &numeric_key, 4);

    // STK = s1(TK, Srand, Mrand) [pg 1971]
    // concatenate the lower 8 octets of Srand and MRand
    memcpy(rand + 0, state->srand + 8, 8);
    memcpy(rand + 8, state->mrand + 8, 8);

    aes_block(state->tk, rand, state->stk);
}

        for (numeric_key = 0; numeric_key <= 999999; numeric_key++) {
            calc_confirm(&state, 1, numeric_key, confirm_mrand);
            calc_confirm(&state, 0, numeric_key, confirm_srand);
            r1 = memcmp(state.mconfirm, confirm_mrand, 16);
            r2 = memcmp(state.mconfirm, confirm_srand, 16);
            if (r1 == 0 || r2 == 0) {
                tk_found = 1;
                break;
            }
        }


    // crack TK by generating and testing every possible STK keys using the key generation
    // function s1 (page 1962, BT 4.0 spec)


shorter crack method: assume TK=0

- calc_stk(&dup_state, numeric_key);
	srand
	mrand

	aes_block(state->tk, rand, state->stk);
- calc_session_key(&dup_state);
	skds
	skdm

	aes_block(state->stk, skd, state->session_key);
"""
