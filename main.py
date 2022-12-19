# -*- coding: utf-8 -*-
"""
semgrep: 多语言静态扫描工具
功能: 代码分析
用法: python3 main.py
"""

import os
import json
import yaml
import shutil
import subprocess
import sys

class Semgrep(object):
    def __get_task_params(self):
        """获取需要任务参数
        :return:
        """
        task_request_file = os.environ.get("TASK_REQUEST")
        with open(task_request_file, 'r') as rf:
            task_request = json.load(rf)
        task_params = task_request["task_params"]

        return task_params
    
    def config(self, rules):
        """配置规则
        :langs: 语言
        :rules: 规则
        """
        rules_path = os.path.abspath("./rules")
        relpos = len(rules_path) + 1
        endsuff = [".yaml", ".yml"]
        filelist = []
        for dirpath, _, files in os.walk(rules_path):
            for filename in files:
                if filename.lower().endswith(tuple(endsuff)):
                    filelist.append(os.path.join(dirpath, filename))
        config_rules_path = os.path.abspath("./config_rules")
        if os.path.exists(config_rules_path):
            shutil.rmtree(config_rules_path)
        os.mkdir(config_rules_path)
        for single_file in filelist:
            rel_path = single_file[relpos:]
            file_path = os.path.join(config_rules_path, rel_path)
            with open(single_file,'r') as fp:
                data = yaml.load(fp, Loader=yaml.FullLoader)
            if data:
                if data.__contains__('rules'):
                    for rule_data in data['rules']:
                        if rule_data["id"] in rules:
                            if not os.path.exists(os.path.dirname(file_path)):
                                os.makedirs(os.path.dirname(file_path))
                            shutil.copy(single_file, file_path)
                            break
        return config_rules_path

    def run(self):
        """
        :return:
        """
        # 代码目录直接从环境变量获取
        source_dir = os.environ.get("SOURCE_DIR", None)
        print("[debug] source_dir: %s" % source_dir)
        # 结果目录直接从环境变量获取
        result_dir = os.environ.get("RESULT_DIR", os.getcwd())
        # 其他参数从task_request.json文件获取
        task_params = self.__get_task_params()
        # 环境变量
        envs = task_params["envs"]
        print("[debug] envs: %s" % envs)

        # 使用机器环境安装的Python
        # 2022-12-02更新，tca自带python3安装semgrep
        path_str = os.environ["PATH"]
        path_list = path_str.split(os.pathsep)
        new_path_list = []
        for path in path_list:
            # if "linux-Python-v3.7.2" in path or "mac-Python-v3.7.0" in path or "win-Python-v3.7.0" in path:
                # continue
            new_path_list.append(path)
        new_path_str = os.pathsep.join(new_path_list)
        os.environ.update({"PATH": new_path_str})
        print("[debug] PATH: %s" % new_path_str)

        # 过滤路径(通配符)
        exclude_path = task_params["path_filters"]["exclusion"]
        include_path = task_params["path_filters"]["inclusion"]
        # 规则
        rules = task_params["rules"]

        # ------------------------------------------------------------------ #
        # 增量扫描时,可以通过环境变量获取到diff文件列表,只扫描diff文件,减少耗时
        # 此处获取到的diff文件列表,已经根据项目配置的过滤路径过滤
        # ------------------------------------------------------------------ #
        # 从 DIFF_FILES 环境变量中获取增量文件列表存放的文件(全量扫描时没有这个环境变量)
        diff_file_json = os.environ.get("DIFF_FILES")
        scan_file_json = os.environ.get("SCAN_FILES")
        if diff_file_json:  # 如果存在 DIFF_FILES, 说明是增量扫描, 直接获取增量文件列表
            print("get diff file: %s" % diff_file_json)
            with open(diff_file_json, "r") as rf:
                diff_files = json.load(rf)
                scan_files = [path for path in diff_files]
        else:
            if os.environ.get("TCA_QUICK_SCAN") and scan_file_json:
                print("get scan file: %s" % scan_file_json)
                with open(scan_file_json, "r") as rf:
                    files = json.load(rf)
                    scan_files = [path for path in files]
            else:  # 未获取到环境变量,即全量扫描,遍历source_dir获取需要扫描的文件列表
                scan_files = [source_dir]
        if len(" ".join(scan_files)) > 100000:
            scan_files = [source_dir]

        if not self.check_tool_version():
            return

        # 设置配置文件、输出文件和结果文件
        config_rules = self.config(rules)
        error_output = os.path.join(result_dir, "error_output.json")
        result=[]

        cmd = [
            "python3",
            "-m",
            "semgrep",
            "scan",
            "--config",
            config_rules,
            "--no-git-ignore",
            "--no-rewrite-rule-ids",
            "--json",
            "--output",
            error_output
        ]

        if include_path:
            include = ["--include='%s'" % path for path in include_path]
            cmd.extend(include)
        if exclude_path:
            exclude = ["--exclude='%s'" % path for path in exclude_path]
            cmd.extend(exclude)

        if not scan_files:
            print("[error] File list is empty.")
            with open("result.json", "w") as fp:
                json.dump(result, fp, indent=2)
            return
        cmd.extend(scan_files)

        scan_cmd = " ".join(cmd)
        print("[debug] cmd: %s" % scan_cmd)
        # 优化调用方式
        subproc = subprocess.Popen(scan_cmd, shell=True)
        subproc.communicate()
        # subprocess.check_output(cmd)

        print("start data handle")
        # 数据处理
        try:
            with open(error_output, "r") as f:
                outputs_data = json.load(f)
        except:
            print("[error] Resulting file not found or cannot be loaded")
            with open("result.json", "w") as fp:
                json.dump(result, fp, indent=2)
            return

        if outputs_data:
            if(len(outputs_data['errors']) > 0):
                error = outputs_data['errors'][0]
                print("[error]: %s" % json.dumps(error, indent=2))
            for item in outputs_data['results']:
                issue = {}
                issue['path'] = item['path']
                issue['line'] = item['start']['line']
                issue['column'] = item['start']['col']
                issue['msg'] = item['extra']['message']
                rule_name = item['check_id']
                if rule_name not in rules:
                    continue
                issue['rule'] = rule_name
                issue['refs'] = []
                if issue != {}:
                    result.append(issue)

        # 输出结果到指定的json文件
        result_path = os.path.join(result_dir, "result.json")
        with open(result_path, "w") as fp:
            json.dump(result, fp, indent=2)

    def check_tool_version(self):
        """
        检查semgrep是否安装以及安装版本，需要升级到0.100.0
        """
        if sys.platform in ("win32"):
            print("[error] Semgrep can not be installed in windows")
            return False
        version_line = ""
        cmd = ["python3", "-m", "semgrep", "--version"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            for line in p.stdout:
                line = bytes.decode(line.strip())
                if line.startswith("0."):
                    version_line = line
        finally:
            p.terminate()
            p.wait()
        if p.returncode == 0:
            if len(version_line) > 0:
                print("[debug] semgrep version: %s" % version_line)
                version = int(version_line.split(".")[1])
                if version < 100:
                    print("[error] Due to rule update, please upgrade semgrep to version 0.100.0, command: python3 -m pip install --upgrade semgrep==0.100.0")
                    return False
                else:
                    return True
        print("[error] Semgrep should be installed locally, command: python3 -m pip install semgrep==0.100.0")
        return False

if __name__ == '__main__':
    print("-- start run tool ...")
    Semgrep().run()
    print("-- end ...")