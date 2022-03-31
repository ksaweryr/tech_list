document.addEventListener('alpine:init', () => {
    Alpine.data('technologies', (author = '') => ({
        async getItems(args) {
            const params = {...args, ord: args.dir + args.ord, off: args.page * args.count};
            delete params.dir;
            delete params.page;
            const result = await apiRequest(`technology?${urlParams(params)}`, {}, 'GET');
            if(result.status != 200) {
                this.error = result.json.error;
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
            dir: '-',
            ...(author === '' || {author})
        },
        data: null,
        error: null,
        selectedTechnology: null,
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
        edit(tid) {
            window.location.href = `/technology/edit/${tid}`;
        },
        showDeletionModal(t) {
            this.selectedTechnology = t;
            (new bootstrap.Modal(document.querySelector('#deletionModal'), {})).show();
        },
        async deleteTechnology(tid) {
            const result = await apiRequest(`technology/${tid}`, {}, 'DELETE');

            if(result.status != 200) {
                this.error = result.json.error;
                this.showError();
                return;
            }

            await this.getItems(this.metadata);
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