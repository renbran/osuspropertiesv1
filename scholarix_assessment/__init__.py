# -*- coding: utf-8 -*-
from . import models
from . import wizards
from . import controllers
from . import hooks

# Expose post_init_hook at module level for Odoo to find it
from .hooks import post_init_hook
