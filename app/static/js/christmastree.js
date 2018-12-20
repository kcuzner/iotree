/**
 * Christmas Tree Control
 */

Vue.directive('click-outside', {
    bind: function (el, binding, vnode) {
        el.clickOutsideEvent = function (ev) {
            if (!(el === ev.target || el.contains(ev.target))) {
                vnode.context[binding.expression](ev);
            }
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
    },
    unbind: function (el) {
        document.body.removeEventListener('click', el.clicnOutsideEvent);
    },
});

Vue.directive('tooltip', {
    bind: function (el, binding) {
        $(el).tooltip({
            title: binding.value,
            placement: binding.arg,
            trigger: 'focus',
        });
    }
});

Vue.component('vue-dropdown-menu', {
    template: '<div class="btn-group" v-click-outside="close"><div class="dropdown" :class="{\'show\': open}">'+
        '<button type="button" class="btn btn-light dropdown-toggle" @click="open = !open" v-html="title"></button>' +
        '<ul class="dropdown-menu" :class="{\'show\': open}">' +
        '<li v-for="(option, i) in options"><a class="dropdown-item" @click="click(option)" v-html="option.value"></a></li>' +
        '</ul>'+
        '</div></div>',
    props: {
        open: {
            type: Boolean,
            default: false,
        },
        options: {
            type: Array,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
    },
    data: function() {
        return {}
    },
    methods: {
        click: function (option) {
            this.$emit('selected', option);
            this.close();
        },
        close: function () {
            this.open = false;
        },
    },
});

var patctl = new Vue({
    el: '#pattern-control',
    data: {
        showHelp: false,
        presets: [{
            value: 'Random Hues',
            data: [{'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },
                {'type': 'random-hue', 'step': 0.002 },],
        }, {
            value: 'Light Chase',
            data: [{'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]},],
        }, {
            value: 'You know what it is...',
            data: [{'type': 'keyframe', 'keys': [
                {'r': 255, 'g': 255, 'b': 0, 'steps': 6, 'type': 'wall'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 6, 'type': 'wall'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 6, 'type': 'wall'},
                {'r': 255, 'g': 255, 'b': 0, 'steps': 6, 'type': 'wall'},
            ]},],
        }, {
            value: 'Triple Chase',
            data: [{'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 255, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 255, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 255, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 255, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 255, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]}, {'type': 'keyframe', 'keys': [
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 255, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'},
                {'r': 0, 'g': 255, 'b': 0, 'steps': 10, 'type': 'sine'},
            ]},],
        },],
        pattern: [],
        ledTypes: [{
            value: '<i class="fa fa-lightbulb color-random"></i> Random Hue',
            data: 'random-hue',
        }, {
            value: '<i class="fa fa-film"></i> Keyframe',
            data: 'keyframe',
        },],
        transitionTypes: [{
            value: 'Sine',
            data: 'sine',
        }, {
            value: 'Linear',
            data: 'linear',
        }, {
            value: 'Wall',
            data: 'wall',
        },],
    },
    methods: {
        load: function (preset) {
            this.pattern = preset.data;
        },
        send: function () {
            if (!this.pattern.length)
                return;

            $.ajax({
                type: 'POST',
                url: pathPrefix + 'pattern',
                contentType: 'application/json',
                data: JSON.stringify(this.pattern),
            }).done(function () {
            }).fail(function () {
                console.log('fail', arguments);
            });
        },
        colorof: function (keyframe) {
            var r = _.clamp(keyframe['r'], 0, 255);
            var g = _.clamp(keyframe['g'], 0, 255);
            var b = _.clamp(keyframe['b'], 0, 255);
            var tohex = function (v) {
                var str = v.toString(16);
                if (str.length % 2) {
                    str = '0' + str;
                }
                return str;
            }
            return '#' + tohex(r) + tohex(g) + tohex(b);
        },
        setColor: function (frame, ev) {
            var r = _.parseInt(ev.target.value.slice(1, 3), 16);
            var g = _.parseInt(ev.target.value.slice(3, 5), 16);
            var b = _.parseInt(ev.target.value.slice(5, 7), 16);
            Vue.set(frame, 'r', r);
            Vue.set(frame, 'g', g);
            Vue.set(frame, 'b', b);
        },
        addLed: function () {
            var led = {'type': 'random-hue', 'step': 0.002};
            this.pattern.push(led);
        },
        removeLed: function (index) {
            this.pattern.splice(index, 1);
        },
        ledTitle: function (led) {
            if (led.type == 'keyframe') {
                return 'Type: <i class="fa fa-film"></i>';
            }
            else if (led.type == 'random-hue') {
                return 'Type: <i class="fa fa-lightbulb color-random"></i>';
            }
            else {
                return '<code>' + led.type + '</code>';
            }
        },
        setType: function (led, type) {
            Vue.set(led, 'type', type.data);
            if (led.type == 'keyframe') {
                if (!('keys' in led) || !led.keys.length) {
                    Vue.set(led, 'keys', [{ 'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'}]);
                }
            }
        },
        addFrame: function (led) {
            if (!('keys' in led)) {
                Vue.set(led, 'keys', []);
            }
            led.keys.push({'r': 255, 'g': 0, 'b': 0, 'steps': 10, 'type': 'sine'});
        },
        removeFrame: function (led, index) {
            led.keys.splice(index, 1);
        },
        transitionTitle: function (frame) {
            return frame.type == 'sine' ? 'Sine' :
                frame.type == 'linear' ? 'Linear' :
                frame.type == 'wall' ? 'Wall' :
                'Unknown';
        },
        setTransition: function (frame, type) {
            Vue.set(frame, 'type', type.data);
        },
    },
});

