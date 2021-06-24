# ------------------ Imports ------------------
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_security import Security
from flask_assets import Environment, Bundle
from flask_uploads import UploadSet, IMAGES
from flask_mail import Mail
from flask_praetorian import Praetorian
from flask_msearch import Search

# ------------------ module variables ------------------
db = SQLAlchemy()

img_set = UploadSet('images', IMAGES)

mail = Mail()

login_manager = LoginManager()

assets = Environment()

security = Security()

guard = Praetorian()

search = Search()

assets = Environment()

js_main_bundle = Bundle('js/main/src/confirm.js', 'js/main/src/pass.js', 'js/main/src/novalidate.js',
                   filters='jsmin', output="js/main/dist/main.min.js") 

edit_profile_js_bundle = Bundle('js/ext/admin/accounts/edit_profile/src/element.js', 'js/ext/admin/main/navalign.js',
                                filters='jsmin', output='js/ext/admin/accounts/edit_profile/dist/index.min.js')

alert_css_bundle = Bundle('styles/alert_css/src/box.css', 'styles/alert_css/src/error.css', 
                    'styles/alert_css/src/info.css', 'styles/alert_css/src/success.css',
                    'styles/alert_css/src/warning.css', filters='cssmin', 
                    output='styles/alert_css/dist/alerts.min.css')

admin_home_css_bundle = Bundle('styles/admin/index/src/index.css', 'styles/admin/util/scrollbar/scrollbar.css',
                               'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css', 
                               filters='cssmin', output='styles/admin/index/dist/index.min.css')

admin_main_accounts_css_bundle = Bundle('styles/admin/accounts/main/src/index.css', 'styles/admin/util/scrollbar/scrollbar.css',
                                  'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css',
                                  filters='cssmin', output='styles/admin/accounts/main/dist/index.min.css')

admin_edit_profile_accounts_css_bundle = Bundle('styles/admin/accounts/edit_profiles/src/edit_profile.css', 'styles/admin/util/scrollbar/scrollbar.css',
                                                'styles/admin/util/navbar/navbar.css', 'styles/admin/util/management/management.css',
                                                filters='cssmin', output='styles/admin/accounts/edit_profiles/dist/edit_profile.min.css')

assets.register('main__js', js_main_bundle)

assets.register('edit_prof_main_js', edit_profile_js_bundle)
  
assets.register('alert__css', alert_css_bundle)

assets.register('admin_dashboard_css', admin_home_css_bundle)

assets.register('admin_main_accounts_css', admin_main_accounts_css_bundle)

assets.register('admin_edit_accounts_css', admin_edit_profile_accounts_css_bundle)

