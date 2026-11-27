// 종이인형 카드의 두께(옆면): 그림 테두리 모양만 남기고 종이 색으로 칠한다.
shader_type spatial;
render_mode cull_disabled;

uniform sampler2D shape_tex : source_color, filter_linear_mipmap;
// 뒷면 그림 (카드 뒤에서 보면 좌우가 바뀌므로 u를 뒤집어 읽음). 앞·뒤 모양이 겹치는 곳만 두께를 그림
uniform sampler2D back_tex : source_color, filter_linear_mipmap;
uniform bool use_back = false;
uniform vec4 edge_color : source_color = vec4(0.93, 0.9, 0.84, 1.0);

void fragment() {
	float a = texture(shape_tex, UV).a;
	if (use_back) {
		a = min(a, texture(back_tex, vec2(1.0 - UV.x, UV.y)).a);
	}
	if (a < 0.5) {
		discard;
	}
	ALBEDO = edge_color.rgb;
	ROUGHNESS = 1.0;
}
