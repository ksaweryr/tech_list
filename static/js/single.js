document.addEventListener('alpine:init', () => {
    Alpine.data('technology', tid => ({
        tid,
        t: null,
        found: true,
        i: null,
        error: null,
        async load() {
            const result = await apiRequest(`technology/${this.tid}`, {}, 'GET');
            if(result.status != 200 && result.status != 404) {
                this.error = likeResult.json.error;
                this.showError();
                return;
            }
            this.found = result.status != 404;
            this.t = Object.assign(result.json, { tid });
        },
        async like() {
            const likeResult = await apiRequest(`technology/like/${this.tid}`, {}, 'POST');
            if(likeResult.status != 200) {
                this.error = likeResult.json.error;
                this.showError();
                return;
            }
            const result = await apiRequest(`technology/${this.tid}`, {}, 'GET');
            this.t = result.json;
        },
        showError() {
            (new bootstrap.Modal(document.querySelector('#errorModal'), {})).show();
        }
    }));
});