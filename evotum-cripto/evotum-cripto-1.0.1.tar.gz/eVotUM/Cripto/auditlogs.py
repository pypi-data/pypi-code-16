# coding: latin-1

###############################################################################
# eVotUM - Electronic Voting System
#
# auditlogs.py
#
# Cripto-3.0.0 - Auditable logs functions
#
# Copyright (c) 2016 Universidade do Minho
# Developed by André Baptista - Devise Futures, Lda. (andre.baptista@devisefutures.com)
# Reviewed by Ricardo Barroso - Devise Futures, Lda. (ricardo.barroso@devisefutures.com)
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
###############################################################################

"""
A log is perhaps the simplest possible storage abstraction. It is an append-only,
totally-ordered sequence of records/entries ordered by time that have a specific
purpose: to record what happened and when.
Logs are usually kept in log files or databases. In the event that an attacker access
the log, it's necessary to limit his ability to corrupt the log entries.

The following functions can be used to generate a SHA256 hash (and verify it) for
each log entry, being that each log entry allows to verify that the previous log
entries were not compromised. So it's possible to guarantee that if an attacker
compromises the log entries, modifying, destroying or creating a new entry,
it can be easily detected/verified and audited.

An auditable log is a sequence of log entries represented by 'log entry N - hash1 N'
where:
  * log entry N - Nth log entry
  * hash1 N - HMAC-SHA256(secret key, ( SHA256 (log entry N) + (hash 1 (N - 1)) )
  * + - concatenation
For N == 1 (first log entry), hash 1 (N-1) == "" (empty)

Important: the secret key MUST NOT be stored in the same place as the log entries.
"""

from eVotUM.Cripto import hashfunctions

#Cripto-3.1.0
def generateLogEntryHash(text, lastEntryHash, secret):
    """
    Generate SHA256 hash for log entry N (text).

    Args:
        text (str): log entry N
        lastEntryHash (hex): (hash 1 (N - 1))
        secret (str): secret key
    Returns:
        hash1 N (hex), i.e., HMAC-SHA256(secret key, ( SHA256 (log entry N) + (hash 1 (N - 1)) ).
    """
    sha256Hash = hashfunctions.generateSHA256Hash(text)
    return hashfunctions.generateHMAC(sha256Hash + lastEntryHash, secret)

#Cripto-3.2.0
def verifyLogEntry(text, logEntryHash, lastEntryHash, secret):
    """
    Verifies log entry N (text).

    Args:
        text (str): log entry N
        logEntryHash (hex): hash1 N
        lastEntryHash (hex): (hash 1 (N - 1))
        secret (str): secret key used to generate hash1 N
    Returns:
        True if logEntryHash == HMAC-SHA256(secret key, ( SHA256 (log entry N) + (hash 1 (N - 1)) ); False otherwise.
    """
    return (logEntryHash == generateLogEntryHash(text, lastEntryHash, secret))
