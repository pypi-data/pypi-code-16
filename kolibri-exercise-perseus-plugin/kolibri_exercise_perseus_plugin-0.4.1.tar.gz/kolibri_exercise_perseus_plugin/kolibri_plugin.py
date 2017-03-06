from __future__ import absolute_import, print_function, unicode_literals

from kolibri.core.webpack import hooks as webpack_hooks
from kolibri.plugins.base import KolibriPluginBase
from kolibri.plugins.learn import hooks


class ExercisePerseusRenderPlugin(KolibriPluginBase):
    pass


class ExercisePerseusRenderAsset(webpack_hooks.WebpackBundleHook):
    unique_slug = "exercise_perseus_render_module"
    src_file = "assets/src/module.js"
    events = {
        "content_render:exercise/perseus": "render"
    }


class ExercisePerseusRenderInclusionHook(hooks.LearnAsyncHook):
    bundle_class = ExercisePerseusRenderAsset
