
import logging
from pynicotine.pluginsystem import BasePlugin

log = logging.getLogger(__name__)

class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.info("BanOnSharedFilesPlugin initialized!")
        self.probed_users = {} # To keep track of users whose stats we've requested

    def enable(self):
        log.info("BanOnSharedFilesPlugin enabled.")

    def disable(self):
        log.info("BanOnSharedFilesPlugin disabled.")

    def upload_queued_notification(self, user, virtual_path, real_path):
        # This event is triggered when a user starts downloading from us.
        # Request user stats to check their shared files/folders.
        if user not in self.probed_users:
            log.info(f"Download queued from user: {user}. Requesting user stats.")
            self.probed_users[user] = "requesting_stats"
            self.core.users.request_user_stats(user)

    def user_stats_notification(self, user, stats):
        # This event is triggered when user stats are received.
        if user in self.probed_users and self.probed_users[user] == "requesting_stats":
            num_files = stats.get("files", 0)
            num_folders = stats.get("dirs", 0)
            ip_address = stats.get("ip", None) # Assuming 'ip' is available in stats

            log.info(f"Received stats for user {user}: {num_files} files, {num_folders} folders.")

            if num_files == 1000 and num_folders == 50:
                log.warning(f"Banning user {user} (IP: {ip_address}) due to exact shared items count.")
                self.core.network_filter.ban_user(user)
                if ip_address:
                    self.core.network_filter.ban_user_ip(ip_address=ip_address)
            else:
                log.info(f"User {user} does not meet exact sharing criteria. Not banning.")
            
            self.probed_users[user] = "processed" # Mark as processed to avoid re-banning

def get_plugin_class():
    return Plugin
