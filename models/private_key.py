# Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
# for details. All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.

from google.appengine.ext import db

class PrivateKey(db.Model):
    """A singleton model that stores the Google API private key for this app.

    This key has to be stored in the database so that it's inaccessible to
    anyone reading the source code, but easily available to the actual App
    Engine instance.

    For anyone with admin rights to the main pub.dartlang.org, the private key
    is available from the App Engine datastore viewer. For anyone creating a new
    package host, a private key can be obtained from the Google API console as
    described in https://developers.google.com/console/help/#WhatIsKey.
    """

    value = db.TextProperty(required=True)
    """The private key, in PEM format."""

    @classmethod
    def set(cls, value):
        """Sets the value of the private key."""
        cls(key_name='singleton', value=value).put()

    @classmethod
    def get(cls):
        """Gets the value of the private key."""
        instance = cls.get_by_key_name('singleton')
        return instance and instance.value

    @classmethod
    def sign(cls, string):
        """Returns the signature of a string.

        This signature is generated using the singleton private key, then
        base64-encoded. It's of the form expected by Google Cloud Storage query
        string authentication. See
        https://developers.google.com/storage/docs/accesscontrol#Signed-URLs.
        """

        # All Google API keys have "notasecret" as their passphrase
        value = cls.get()
        if value is None: raise "Private key has not been set."
        key = RSA.importKey(value, passphrase='notasecret')
        # TODO(nweiz): This currently doesn't work locally without modifying
        # google/appengine/tools/dev_appserver_import_hook.py by adding
        # 'AESCipher', 'blockalgo', and '_AES' to the
        # __CRYPTO_CIPHER_ALLOWED_MODULES constant. I haven't tested whether it
        # works on the remote server or not.
        return base64.b64encode(PKCS1_v1_5.new(key).sign(SHA256.new(string)))
