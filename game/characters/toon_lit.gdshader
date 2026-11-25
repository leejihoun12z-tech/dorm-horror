shader_type spatial;
// 옅은 툰 (Family Time 느낌): 그려 넣은 텍스처 + 그림자 1단.
// 빛을 받는 셰이더라 밤 손전등이 그대로 먹는다 (tech-plan §5-4).
// 얼굴 그림처럼 투명한 곳이 있는 텍스처도 같은 셰이더로 (알파 잘라내기).

uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, hint_default_white;
uniform vec4 tint : source_color = vec4(1.0);
// 그림자 쪽 밝기 (0 = 새까맣게, 1 = 그림자 없음)
uniform float shade_floor : hint_range(0.0, 1.0) = 0.55;
// 밝은 면/그림자 경계 위치와 부드러움
uniform float band_threshold : hint_range(0.0, 1.0) = 0.45;
uniform float band_softness : hint_range(0.0, 0.5) = 0.06;

void fragment() {
	vec4 c = texture(albedo_tex, UV) * tint;
	ALBEDO = c.rgb;
	ALPHA = c.a;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
}

void light() {
	float half_lambert = dot(NORMAL, LIGHT) * 0.5 + 0.5;
	float band = smoothstep(band_threshold - band_softness, band_threshold + band_softness, half_lambert);
	float lit = mix(shade_floor, 1.0, band);
	DIFFUSE_LIGHT += lit * ATTENUATION * LIGHT_COLOR / PI;
}
