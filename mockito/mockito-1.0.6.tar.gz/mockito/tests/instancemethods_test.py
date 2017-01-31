# Copyright (c) 2008-2016 Szczepan Faber, Serhiy Oplakanets, Herr Kaste
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import pytest

from .test_base import TestBase
from mockito import (
    mock, when, expect, unstub, ANY, verify, verifyNoMoreInteractions,
    verifyZeroInteractions, verifyNoUnwantedInteractions,
    verifyStubbedInvocationsAreUsed)
from mockito.invocation import InvocationError
from mockito.verification import VerificationError

pytestmark = pytest.mark.usefixtures("unstub")

class Dog(object):
    def waggle(self):
        return "Wuff!"

    def bark(self, sound):
        return "%s!" % sound

    def do_default_bark(self):
        return self.bark('Wau')

    def __call__(self):
        pass

class InstanceMethodsTest(TestBase):
    def tearDown(self):
        unstub()

    def testUnstubClassMethod(self):
        original_method = Dog.waggle
        when(Dog).waggle().thenReturn('Nope!')

        unstub()

        rex = Dog()
        self.assertEquals('Wuff!', rex.waggle())
        self.assertEquals(original_method, Dog.waggle)

    def testUnstubMockedInstanceMethod(self):
        rex = Dog()
        when(rex).waggle().thenReturn('Nope!')
        assert rex.waggle() == 'Nope!'
        unstub()
        assert rex.waggle() == 'Wuff!'

    def testUnstubMockedInstanceDoesNotHideTheClass(self):
        when(Dog).waggle().thenReturn('Nope!')
        rex = Dog()
        when(rex).waggle().thenReturn('Sure!')
        assert rex.waggle() == 'Sure!'

        unstub()
        assert rex.waggle() == 'Wuff!'


    def testStubAnInstanceMethod(self):
        when(Dog).waggle().thenReturn('Boing!')

        rex = Dog()
        self.assertEquals('Boing!', rex.waggle())

    def testStubsAnInstanceMethodWithAnArgument(self):
        when(Dog).bark('Miau').thenReturn('Wuff')

        rex = Dog()
        self.assertEquals('Wuff', rex.bark('Miau'))

    def testInvokeAStubbedMethodFromAnotherMethod(self):
        when(Dog).bark('Wau').thenReturn('Wuff')

        rex = Dog()
        self.assertEquals('Wuff', rex.do_default_bark())
        verify(Dog).bark('Wau')

    def testYouCantStubAnUnknownMethodInStrictMode(self):
        try:
            when(Dog).barks('Wau').thenReturn('Wuff')
            self.fail(
                'Stubbing an unknown method should have thrown a exception')
        except InvocationError:
            pass

    def testStubUnknownMethodInLooseMode(self):
        when(Dog, strict=False).walk()

        rex = Dog()
        rex.walk()

        unstub()
        with pytest.raises(AttributeError):
            rex.walk
        with pytest.raises(AttributeError):
            Dog.walk

    def testAddNewMethodOnInstanceInLooseMode(self):
        rex = Dog()
        when(rex, strict=False).walk()
        rex.walk()

        unstub()
        with pytest.raises(AttributeError):
            rex.walk

    def testThrowEarlyIfCallingWithUnexpectedArgumentsInStrictMode(self):
        when(Dog).bark('Miau').thenReturn('Wuff')
        rex = Dog()
        try:
            rex.bark('Shhh')
            self.fail('Calling a stubbed method with unexpected arguments '
                      'should have thrown.')
        except InvocationError:
            pass

    def testStubCallableObject(self):
        when(Dog).__call__().thenReturn('done')

        rex = Dog()  # <= important. not stubbed
        assert rex() == 'done'

    def testReturnNoneIfCallingWithUnexpectedArgumentsIfNotStrict(self):
        when(Dog, strict=False).bark('Miau').thenReturn('Wuff')
        rex = Dog()
        self.assertEquals(None, rex.bark('Shhh'))

    def testStubInstancesInsteadOfClasses(self):
        rex = Dog()
        when(rex).bark('Miau').thenReturn('Wuff')

        self.assertEquals('Wuff', rex.bark('Miau'))
        verify(rex, times=1).bark(ANY)

        max = Dog()
        self.assertEquals('Miau!', max.bark('Miau'))

    def testUnstubInstance(self):
        rex = Dog()
        when(rex).bark('Miau').thenReturn('Wuff')

        unstub()

        assert rex.bark('Miau') == 'Miau!'


    def testNoExplicitReturnValueMeansNone(self):
        when(Dog).bark('Miau').thenReturn()
        rex = Dog()

        self.assertEquals(None, rex.bark('Miau'))

    def testForgottenThenReturnMeansReturnNone(self):
        when(Dog).bark('Miau')
        when(Dog).waggle()
        rex = Dog()

        self.assertEquals(None, rex.bark('Miau'))
        self.assertEquals(None, rex.waggle())

class TestVerifyInteractions:
    class TestZeroInteractions:
        def testVerifyNoMoreInteractionsWorks(self):
            when(Dog).bark('Miau')
            verifyNoMoreInteractions(Dog)

        def testVerifyZeroInteractionsWorks(self):
            when(Dog).bark('Miau')
            verifyZeroInteractions(Dog)

    class TestOneInteraction:
        def testNothingVerifiedVerifyNoMoreInteractionsRaises(self):
            when(Dog).bark('Miau')
            rex = Dog()
            rex.bark('Miau')
            with pytest.raises(VerificationError):
                verifyNoMoreInteractions(Dog)

        def testIfVerifiedVerifyNoMoreInteractionsPasses(self):
            when(Dog).bark('Miau')
            rex = Dog()
            rex.bark('Miau')
            verify(Dog).bark('Miau')
            verifyNoMoreInteractions(Dog)

        def testNothingVerifiedVerifyZeroInteractionsRaises(self):
            when(Dog).bark('Miau')
            rex = Dog()
            rex.bark('Miau')
            with pytest.raises(VerificationError):
                verifyZeroInteractions(Dog)

        def testIfVerifiedVerifyZeroInteractionsStillRaises(self):
            when(Dog).bark('Miau')
            rex = Dog()
            rex.bark('Miau')
            verify(Dog).bark('Miau')
            with pytest.raises(VerificationError):
                verifyZeroInteractions(Dog)

class TestEnsureStubsAreUsed:
    def testBarkOnUnusedStub(self):
        when(Dog).bark('Miau')
        with pytest.raises(VerificationError):
            verifyStubbedInvocationsAreUsed(Dog)

    def testPassUsedOnce(self):
        when(Dog).bark('Miau')
        rex = Dog()
        rex.bark('Miau')
        verifyStubbedInvocationsAreUsed(Dog)

    def testFailSecondStubNotUsed(self):
        when(Dog).bark('Miau')
        when(Dog).waggle()
        rex = Dog()
        rex.bark('Miau')
        with pytest.raises(VerificationError):
            verifyStubbedInvocationsAreUsed(Dog)

    def testFailSecondStubSameMethodUnused(self):
        when(Dog).bark('Miau')
        when(Dog).bark('Grrr')
        rex = Dog()
        rex.bark('Miau')
        with pytest.raises(VerificationError):
            verifyStubbedInvocationsAreUsed(Dog)

    def testPassTwoStubsOnSameMethodUsed(self):
        when(Dog).bark('Miau')
        when(Dog).bark('Grrr')
        rex = Dog()
        rex.bark('Miau')
        rex.bark('Grrr')
        verifyStubbedInvocationsAreUsed(Dog)

    def testPassOneCatchAllOneSpecificStubBothUsed(self):
        when(Dog).bark(Ellipsis)
        when(Dog).bark('Miau')
        rex = Dog()
        rex.bark('Miau')
        rex.bark('Grrr')
        verifyStubbedInvocationsAreUsed(Dog)

    def testFailSecondAnswerUnused(self):
        when(Dog).bark('Miau').thenReturn('Yep').thenReturn('Nop')
        rex = Dog()
        rex.bark('Miau')
        with pytest.raises(VerificationError):
            verifyStubbedInvocationsAreUsed(Dog)


@pytest.mark.usefixtures('unstub')
class TestImplicitVerificationsUsingExpect:

    @pytest.fixture(params=[
        {'times': 2},
        {'atmost': 2},
        {'between': [1, 2]}
    ], ids=['times', 'atmost', 'between'])
    def verification(self, request):
        return request.param

    def testFailImmediatelyIfWantedCountExceeds(self, verification):
        rex = Dog()
        expect(rex, **verification).bark('Miau').thenReturn('Wuff')
        rex.bark('Miau')
        rex.bark('Miau')

        with pytest.raises(InvocationError):
            rex.bark('Miau')

    def testVerifyNoMoreInteractionsWorks(self, verification):
        rex = Dog()
        expect(rex, **verification).bark('Miau').thenReturn('Wuff')
        rex.bark('Miau')
        rex.bark('Miau')

        verifyNoMoreInteractions(rex)

    def testNoUnwantedInteractionsWorks(self, verification):
        rex = Dog()
        expect(rex, **verification).bark('Miau').thenReturn('Wuff')
        rex.bark('Miau')
        rex.bark('Miau')

        verifyNoUnwantedInteractions(rex)

    @pytest.mark.parametrize('verification', [
        {'times': 2},
        {'atleast': 2},
        {'between': [1, 2]}
    ], ids=['times', 'atleast', 'between'])
    def testVerifyNoMoreInteractionsBarksIfUnsatisfied(self, verification):
        rex = Dog()
        expect(rex, **verification).bark('Miau').thenReturn('Wuff')

        with pytest.raises(VerificationError):
            verifyNoMoreInteractions(rex)

    @pytest.mark.parametrize('verification', [
        {'times': 2},
        {'atleast': 2},
        {'between': [1, 2]}
    ], ids=['times', 'atleast', 'between'])
    def testNoUnwantedInteractionsBarksIfUnsatisfied(self, verification):
        rex = Dog()
        expect(rex, **verification).bark('Miau').thenReturn('Wuff')

        with pytest.raises(VerificationError):
            verifyNoUnwantedInteractions(rex)

    def testNoUnwantedInteractionsForAllRegisteredObjects(self):
        rex = Dog()
        mox = Dog()

        expect(rex, times=1).bark('Miau')
        expect(mox, times=1).bark('Miau')

        rex.bark('Miau')
        mox.bark('Miau')

        verifyNoUnwantedInteractions()

    def testUseWhenAndExpectTogetherVerifyNoUnwatedInteractions(self):
        rex = Dog()
        when(rex).waggle()
        expect(rex, times=1).bark('Miau')

        rex.waggle()
        rex.bark('Miau')

        verifyNoUnwantedInteractions()

    def testExpectWitoutVerification(self):
        rex = Dog()
        expect(rex).bark('Miau').thenReturn('Wuff')
        verifyNoMoreInteractions(rex)

        rex.bark('Miau')
        with pytest.raises(VerificationError):
            verifyNoMoreInteractions(rex)

    # Where to put this test? During first implementation I broke this
    def testEnsureWhenGetsNotConfused(self):
        m = mock()
        when(m).foo(1).thenReturn()
        m.foo(1)
        with pytest.raises(VerificationError):
            verifyNoMoreInteractions(m)

    def testEnsureMultipleExpectsArentConfused(self):
        rex = Dog()
        expect(rex, times=1).bark('Miau').thenReturn('Wuff')
        expect(rex, times=1).waggle().thenReturn('Wuff')
        rex.bark('Miau')
        rex.waggle()

