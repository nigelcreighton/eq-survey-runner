from mock import patch, Mock

from tests.integration.integration_test_case import IntegrationTestCase


class TestApplicationVariables(IntegrationTestCase):

    def setUp(self, setting_overrides=None):

        self.begin_subsegment = patch('aws_xray_sdk.core.xray_recorder.begin_subsegment')
        self.begin_subsegment_mock = self.begin_subsegment.start()
        self.end_subsegment = patch('aws_xray_sdk.core.xray_recorder.end_subsegment')
        self.end_subsegment_mock = self.end_subsegment.start()
        self.XRayMiddleware = patch('aws_xray_sdk.ext.flask.middleware.XRayMiddleware', Mock())
        self.XRayMiddleware_mock = self.XRayMiddleware.start()

        super().setUp({
            'AWS_XRAY_SDK_ENABLED': True
        })

    def tearDown(self):
        super().tearDown()
        self.begin_subsegment.stop()
        self.end_subsegment.stop()
        self.XRayMiddleware.stop()

    def test_xray_tracing_setup(self):
        self.launchSurvey('test', 'textfield')

        self.assertTrue(self.begin_subsegment_mock.called)
        self.assertTrue(self.end_subsegment_mock.called)
        self.assertTrue(self.XRayMiddleware_mock.called)

        self.assertEqual(self.XRayMiddleware_mock.call_count, 1)

        self.assertEqual(self.begin_subsegment_mock.call_count,
                         self.end_subsegment_mock.call_count)

        self.assertStatusOK()
