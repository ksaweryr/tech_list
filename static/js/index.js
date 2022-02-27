document.addEventListener('alpine:init', () => {
    Alpine.data('technologies', () => ({
        async getItems(args) {
            const { page, count, dir, ord } = args;
            const result = await apiRequest(`technology?off=${page * count}&size=${count}&ord=${dir + ord}`, {}, 'GET');
            if(result.status != 200) {
                this.error = likeResult.json.error;
                this.showError();
                return;
            }
            this.data = result.json;
            this.metadata = args;
        },
        metadata: {
            page: 0,
            count: 5,
            ord: 'creation_date',
            dir: '-'
        },
        data: null,
        error: null,
        async changeOrdering(e) {
            document.querySelectorAll('.ordering-selection-button').forEach(e => e.classList.remove('active'));
            e.target.classList.add('active');
            this.getItems(Object.assign(this.metadata, { ord: e.target.name }));
        },
        async toggleDir() {
            const { dir } = this.metadata;
            this.metadata.dir = (dir == '' ? '-' : '');
            this.getItems(this.metadata);
        },
        async like(tid, i) {
            const likeResult = await apiRequest(`technology/like/${tid}`, {}, 'POST');
            if(likeResult.status != 200) {
                this.error = likeResult.json.error;
                this.showError();
                return;
            }
            const result = await apiRequest(`technology/${tid}`, {}, 'GET');
            this.data.results[i] = Object.assign(result.json, { tid });
        },
        async changePage(n) {
            this.metadata.page += n;
            await this.getItems(this.metadata);
        },
        showError() {
            (new bootstrap.Modal(document.querySelector('#errorModal'), {})).show();
        }
    }));
});