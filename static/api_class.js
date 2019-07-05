class Cruise_API {
    constructor() {
        this.xhr = new XMLHttpRequest();
    }

    sendGroupChat(group_id, content) {
        if (!this.checkMessage(content)) {
            return false
        }
        
        this.xhr.open("GET", `/api/post_group?id=${group_id}&content=${content}`, true);
        this.xhr.send();

        return true
    }

    loadGroupChat(group_id, time, callback) {
        this.xhr.onreadystatechange = () => {
            if (this.xhr.status == 200 && this.xhr.readyState == 4) {
                callback(this.xhr.responseText);
            }
        }

        this.xhr.open("GET", `/api/check_group?id=${group_id}&time=${time}`, true);
        this.xhr.send();
    }

    sendDirectChat(user_id, content) {
        if (!this.checkMessage(content)) {
            return false
        }
        
        this.xhr.open("GET", `/api/post_direct?id=${user_id}&content=${content}`, true);
        this.xhr.send();

        return true
    }

    loadDirectChat(user_id, time, callback) {
        this.xhr.onreadystatechange = () => {
            if (this.xhr.status == 200 && this.xhr.readyState == 4) {
                callback(this.xhr.responseText);
            }
        }

        this.xhr.open("GET", `/api/check_direct?id=${user_id}&time=${time}`, true);
        this.xhr.send();
    }

    checkName(str, callback) {
        this.xhr.onreadystatechange = () => {
            if (this.xhr.status == 200 && this.xhr.readyState == 4) {
                callback(this.xhr.responseText);
            }
        }
        post-input
        this.xhr.open("GET", `/api/check_name?string=${str}`, true);
        this.xhr.send();
    }

    checkMessage(str) {
        if (str.length > 250) {
            return false
        }
        if (str.trim().length == 0) {
            return false
        }

        return true
    }

    checkChatCreated(id, callback) {
        this.xhr.onreadystatechange = () => {
            if (this.xhr.status == 200 && this.xhr.readyState == 4) {
                callback(this.xhr.responseText);
            }
        }

        this.xhr.open("GET", `/api/check_direct_chat?id=${id}`, true);
        this.xhr.send();
    }
}