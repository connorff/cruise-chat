class Cruise_API {
    constructor() {
        this.xhr = new XMLHttpRequest();
    }

    checkName(str) {
        this.xhr.open("GET", `/api/check_name?string=${str}`);

        this.xhr.onreadystatechange = () => {
            if (this.status === 200 && this.readystate === 4) {
                return this.responseText;
            }
        }

        this.xhr.send();
    }
}