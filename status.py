    def commit_worker(self):
        """ Send given configuration commands to device """
        app.status_bar.progress_start()
        output, result = '', False
        # Connect to device
        device = {**AuthDialog.resultdict, 'device_type': self.tree.parser.name,
                  'secret': AuthDialog.resultdict['password'], 'ip': self._resolve()}
        try:
            with ConnectHandler(**device) as session:
                # Prompt should match hostname
                output += session.find_prompt()
                if not re.search(self.hostname + '[#>]', output):
                    raise ValueError('Hostname does not match')
                # Enter privileged exec
                if self.tree.parser.name != 'cisco_xr':
                    output += self._enable(session)
                # Configure device
                output += session.send_config_set(self.enqueued)
                if re.search('% Invalid input|% Incomplete command', output):
                    raise ValueError('One or more commands not recognized')
                # Apply/save configuration
                if self.tree.parser.name == 'cisco_xr':
                    output += session.commit(comment=self.comment)
                else:
                    output += session.save_config()
                result = True
        except Exception as e:
            output += '\nERROR: ' + str(e)
        app.con_tab.write(output.strip('\n').replace('\n\n', '\n'), self.fqdn)
        app.con_tab.dump('console.txt')
        app.status_bar.progress_stop()
        return result
